from util import log_event
import util
import config

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from datetime import datetime
import json
import os

MODULE = os.path.basename(__file__)[:-3]

KEYSPACE = 'users'
TABLE_NAMES = {
    'users': 'users',
    'budgets': 'budgets'
}
TABLE_FORMAT = {
    TABLE_NAMES['users']: [
        'username',
        'firstname',
        'lastname'
    ],
    TABLE_NAMES['budgets']: [
        'itemid',
        'total',
        'purchases'
    ]
}

class DataStraxApi:
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
                    lastname text
                );
            """
        )
        self.session.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {KEYSPACE}.{TABLE_NAMES['budgets']} (
                    itemid text PRIMARY KEY,
                    total float,
                    purchases text
                );
            """
        )
        log_event('Loaded users and budgets tables', module=MODULE)

    def get(self, table: str, primary_key: str=None):
        """
        Access data with primary key, or access all data

        Args:
            primary_key (str, optional): Primary key of data to access. Defaults to None.
            table (str): Name of table to access.

        Returns:
            Row (namedTuple): Data accessed
            ResultSet: Data accessed
        """
        if TABLE_NAMES.get(table) is None:
            event_log("Invalid table: {table}", module=MODULE)
            return None
        if primary_key:
            return self.session.execute(f"SELECT * FROM {TABLE_NAMES[table]} WHERE {TABLE_FORMAT[table][0]}=%s", [primary_key]).one()
        return self.session.execute(f"SELECT * FROM {TABLE_NAMES[table]}")

    def insert(self, table: str, data: dict, primary_key: str=None, budget_append: bool=False):
        """
        Insert data into table.

        Args:
            table (str): name of table to insert to.
            data (dict): Data to insert.
            primary_key (str, optional): Primary Key of data. Defaults to None
            budget_append (bool): purchases should be appended

        Returns:
            ResultSet: Response of execution of insertion.
        """
        if TABLE_NAMES.get(table) is None:
            event_log("Invalid table: {table}", module=MODULE)
            return None
        if primary_key is None:
            primary_key = data.get(TABLE_FORMAT.get(table)[0])
            if primary_key is None:
                log_event(f"No primary key for {table} in {data}", module=MODULE)
                return None
        if 'total' in data.keys():
            log_event(f"Attempted to reassign total to {data['total']} manually. Not Allowed.", module=MODULE)
            return None
        if 'purchases' in data.keys():
            item = self.get(TABLE_NAMES[table], primary_key)
            if item is not None:
                purchases = json.loads(item.purchases)
            else:
                purchases = []
            if budget_append:
                new_purchases = data['purchases']
                purchases += new_purchases
            else:
                purchases = data['purchases']
            print(purchases)
            data['total'] = round(sum(purchase['amount'] for purchase in purchases), 2)
            data['purchases'] = json.dumps(purchases)

        response = self.session.execute(
            f"INSERT INTO {TABLE_NAMES[table]} ({', '.join(data)}) VALUES ({'%s, ' * (len(data) - 1) + '%s'})", list(data.values())
        )
        updated_data_string = ', '.join(f'{name}: {value}' for name, value in data.items())
        log_event(f"Inserted {table[:-1]} ({updated_data_string})", module=MODULE)
        return response
    
    def delete(self, table: str, primary_key: str):
        """
        Delete row with primary key.

        Args:
            table (str): Name of table to change.
            primary_key (str): Primary key of row to delete.

        Returns:
            ResultSet: Response of execution of deletion.
        """
        if TABLE_NAMES.get(table) is None:
            event_log("Invalid table", module=MODULE)
            return None
        prepared = self.session.prepare(f"DELETE FROM {TABLE_NAMES[table]} WHERE {TABLE_FORMAT[table][0]}=?")
        response = self.session.execute(prepared, [primary_key])
        log_event(f"Deleted {TABLE_FORMAT[table][0]}: {primary_key}", module=MODULE)
        return response

def main():
    users = {
        'lougene': {'firstname': 'eugene', 'lastname': 'hong'},
        'neiphu': {'firstname': 'andrew', 'lastname': 'hong'}
    }
    db_api = DataStraxApi()
    # insert_response = db_api.insert(TABLE_NAMES['users'], 'neiphu', {'username': 'neiphu', 'firstname': users['neiphu']['firstname'], 'lastname': users['neiphu']['lastname']})
    # db_api.insert(TABLE_NAMES['users'], 'lougene', {'username': 'lougene', 'firstname': users['lougene']['firstname'], 'lastname': users['lougene']['lastname']})
    # get_response = db_api.get(TABLE_NAMES['users'], primary_key='lougene')
    # delete_response = db_api.delete(TABLE_NAMES['users'], 'lougene')
    # get_all_response = db_api.get(TABLE_NAMES['users'])
    item_data = [
        {
            'itemid': util.itemid(datetime.today(), 'food'),
            'purchases': [util.make_purchase('breakfast', -12.36, datetime.today()), util.make_purchase('lunch', -15.75, datetime.today())]
            # 'purchases': [util.make_purchase('dinner', -15.99, datetime.today())]
        },
        {
            'purchases': [util.make_purchase('shirt', -14.99, datetime.today()), util.make_purchase('pants', -20, datetime.today())],
            'itemid': util.itemid(datetime.today(), 'clothes')
        }
    ]
    insert_response = db_api.insert(TABLE_NAMES['budgets'], item_data[0], budget_append=True)
    db_api.insert(TABLE_NAMES['budgets'], item_data[1])
    get_response = db_api.get(TABLE_NAMES['budgets'], primary_key=item_data[1]['itemid'])
    delete_response = db_api.delete(TABLE_NAMES['budgets'], item_data[1]['itemid'])
    get_all_response = db_api.get(TABLE_NAMES['budgets'])
    print(
        f"insert response ({type(insert_response)}): {insert_response}\n"
        f"get response ({type(get_response)}): {get_response}\n"
        f"delete response({type(delete_response)}): {delete_response}\n"
        f"get all response ({type(get_all_response)}): {[response for response in get_all_response]}"
        )

if __name__ == '__main__':
    main()