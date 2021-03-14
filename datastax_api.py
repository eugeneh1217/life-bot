from util import log_event
import util
import config

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from collections import namedtuple
from datetime import datetime
import json
import os

BudgetKey = namedtuple('BudgetKey', ['owner', 'date', 'name'])
LogKey = namedtuple('LogKey', ['owner', 'date'])

MODULE = os.path.basename(__file__)[:-3]

KEYSPACE = 'users'
TABLE_NAMES = {
    'users': 'users',
    'budgets': 'budgets',
    'logs': 'logs'
}
TABLE_FORMAT = {
    TABLE_NAMES['users']: [
        'username',
        'firstname',
        'lastname',
        'budget'
    ],
    TABLE_NAMES['budgets']: [
        "owner text",
        "name text",
        "date text",
        "principle",
        "spent",
        "purchases",
        "PRIMARY KEY (owner, date, name)"
    ]
}

PRIMARY_KEY_PARTS = {'budgets': ['owner', 'date', 'name'], 'logs': ['owner', 'date']}

def validate_table(func):
    def wrapper(*args, **kwargs):
        if TABLE_NAMES.get(args[1]) is None:
            log_event(f"Invalid table: {args[1]}", module=MODULE)
            return None
        return func(*args, **kwargs)
    return wrapper

class DataStaxApi:
    def __init__(self):
        secure_bundle_path = f'{os.path.dirname(os.path.realpath(__file__))}/secure-connect-life-bot-db.zip'
        cloud_config = {
            'secure_connect_bundle': secure_bundle_path
        }
        auth_provider = PlainTextAuthProvider(config.DATASTAX_CLIENT_ID, config.DATASTAX_CLIENT_SECRET)
        cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
        self.session = cluster.connect(KEYSPACE)
        db_version = self.session.execute('select release_version from system.local').one()
        if db_version:
            log_event(f'accessing database version: {db_version[0]}', module=MODULE)
        else:
            log_event('Could not find Version', module=MODULE)

        # create tables if not there
        self.session.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {KEYSPACE}.{TABLE_NAMES['users']} (
                    username text PRIMARY KEY,
                    firstname text,
                    lastname text,
                    budget text
                );
            """
        )
        self.session.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {KEYSPACE}.{TABLE_NAMES['budgets']} (
                    owner text,
                    date text,
                    name text,
                    principle float,
                    spent float,
                    purchases text,
                    PRIMARY KEY (owner, date, name)
                );
            """
        )
        self.session.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {KEYSPACE}.{TABLE_NAMES['logs']} (
                    owner text,
                    date text,
                    content text,
                    PRIMARY KEY (owner, date)
                );
            """
        )
        log_event('Loaded users and budgets tables', module=MODULE)

    @validate_table
    def get(self, table, primary_key=None):
        # access specific key
        if primary_key:
            # print(table)
            if table == 'budgets' or table == 'logs':
                if table == 'budgets':
                    if type(primary_key) is not BudgetKey:
                        log_event(f"Invalid primary key for budgets table: {type(primary_key)}", module=MODULE)
                        return None
                if table == 'logs':
                    if type(primary_key) is not LogKey:
                        log_event(f"Invalid primary key for logs table: {type(primary_key)}", module=MODULE)
                        return None
                attributes = ' AND '.join([key + '=\'' + getattr(primary_key, key) + '\'' for key in PRIMARY_KEY_PARTS[table][:len(primary_key)]])
                print(f"SELECT * FROM users.{TABLE_NAMES[table]} WHERE {attributes} ALLOW FILTERING")
                # return self.session.execute(f"SELECT * FROM {TABLE_NAMES[table]} WHERE {' AND '.join([key + '=%s' for key in PRIMARY_KEY_PARTS[table][:len(primary_key)]])} ALLOW FILTERING", list(primary_key)).one()
                return self.session.execute(f"SELECT * FROM users.{TABLE_NAMES[table]} WHERE {attributes} ALLOW FILTERING").one()

            else:
                return self.session.execute(f"SELECT * FROM {TABLE_NAMES[table]} WHERE {TABLE_FORMAT[table][0]}=%s", [primary_key]).one()
        return self.session.execute(f"SELECT * FROM {TABLE_NAMES[table]}")

    @validate_table
    def insert(self, table: str, data: dict, primary_key=None, budget_append: bool=False):
        # catch attempts to edit spent
        if 'spent' in data.keys():
            log_event(f"Attempted to reassign spent to {data['spent']} manually. Not Allowed.", module=MODULE)
            return None
        # if not budgets, check data for primary_key
        if primary_key is None and table != 'budgets':
            primary_key = data.get(TABLE_FORMAT.get(table)[0])
            if primary_key is None:
                log_event(f"No primary key for {table} in {data}", module=MODULE)
                return None
        # handle editing purchase
        if 'purchases' in data.keys():
            item = self.get(TABLE_NAMES[table], primary_key)
            # check if purchases already there
            if item.purchases is not None:
                purchases = json.loads(item.purchases)
            else:
                purchases = []
            # should we append or replace past purchases
            if budget_append:
                new_purchases = data['purchases']
                purchases += new_purchases
            else:
                purchases = data['purchases']
            # udpate spent and purchases
            data['spent'] = round(sum(purchase['amount'] for purchase in purchases), 2)
            data['purchases'] = json.dumps(purchases)

        response = self.session.execute(
            f"INSERT INTO {TABLE_NAMES[table]} ({', '.join(data)}) VALUES ({'%s, ' * (len(data) - 1) + '%s'})", list(data.values())
        )
        owner = self.get('users', BudgetKey(data['owner'], data['date'], data['name']))
        owner_budget = owner['budget']
        if owner_budget:
            owner_budget = json.loads(owner_budget)
        else:
            owner_budget = []
        owner_budget.append(f"{data['date']} {data['name']}")
        self.insert('users', {'budget': owner_budget}, primary_key=data['owner'])
        updated_data_string = ', '.join(f'{name}: {value}' for name, value in data.items())
        log_event(f"Inserted {table[:-1]} ({updated_data_string})", module=MODULE)
        return response
    
    @validate_table
    def delete(self, table: str, primary_key):
        if table == 'budgets':
            print(f"DELETE FROM {TABLE_NAMES[table]} WHERE {' AND '.join([key + '=%s' for key in PRIMARY_KEY_PARTS[:len(primary_key)]])}, {list(primary_key)}")
            prepared = self.session.prepare(f"DELETE FROM {TABLE_NAMES[table]} WHERE {' AND '.join([key + '=?' for key in PRIMARY_KEY_PARTS[:len(primary_key)]])}")
            response = self.session.execute(prepared, list(primary_key))
        else:
            prepared = self.session.prepare(f"DELETE FROM {TABLE_NAMES[table]} WHERE {TABLE_FORMAT[table][0]}=?")
            response = self.session.execute(prepared, [primary_key])
        log_event(f"Deleted {TABLE_FORMAT[table][0]}: {primary_key}", module=MODULE)
        return response

def main():
    db_api = DataStaxApi()
    print(db_api.get('logs')[0])
    print(db_api.get('logs', primary_key=LogKey('lougene', datetime.today().strftime('%m/%d/%y'))))

    # db_api.insert('budgets', {
    #     'owner': 'lougene',
    #     'name': 'food',
    #     'date': datetime.today().strftime('%m/%Y'),
    #     'principle': 500,
    # })
    # # need to get all three of primary key to insert something
    # db_api.insert('budgets', {
    #     'owner': 'lougene',
    #     'date': '03/2021',
    #     'name': 'food',
    #     'purchases': [util.make_purchase('shirt', -14.99, datetime.today()), util.make_purchase('pants', -20, datetime.today())]
    # }, primary_key=BudgetKey('lougene', '03/2021', 'food'))
    # db_api.delete(
    #     'budgets', primary_key=BudgetKey('lougene', '03/2021', 'food')
    # )


if __name__ == '__main__':
    main()