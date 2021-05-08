from flask import Flask, abort, request, jsonify, g, url_for
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
)

import os

# endpoint references
USER_ENDPOINT_BODY = '/api/users'
RESOURCE_ENDPOINT_BODY = '/api/budgets'

# app configs
app = Flask(__name__)
app.config['SECRET_KEY'] = 'how many woog wiggles does it take to wiggle a woogasaur'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/life_bot.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, lifespan=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=lifespan)
        return s.dumps({'user_id': self.user_id})

    # throws BadSignature and SignatureExpired
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        data = s.loads(token)
        return User.query.get(data['user_id'])

# add new user
@app.route(USER_ENDPOINT_BODY, methods=['POST'])
def add_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400, description=f'Missing arguments')
    if User.query.filter_by(username=username).first() is not None:
        abort(400, description=f'Username [{username}] already exists') # username already exists
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (
        jsonify({'username': user.username}),
        201,
        {'location': url_for('get_all_users', user_id=user.user_id, _external=True)}
    )

@auth.verify_password
def verify_password(username, password_or_token):
    if username == 'token':
        user = User.verify_auth_token(password_or_token)
    else:
        user = User.query.filter_by(username=username).first()
        if not user or not user.verify_password(password_or_token):
            return False
    g.user = user
    return True

# request token
@app.route(f'{USER_ENDPOINT_BODY}/token', methods=['GET'])
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')}), 200

# get all users
@app.route(f'{USER_ENDPOINT_BODY}/all', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.username for user in users]), 200

# get/modify user by user_id
@app.route(f'{USER_ENDPOINT_BODY}/<int:user_id>', methods=['GET', 'DELETE', 'PUT'])
@auth.login_required
def access_user(user_id):
    user = User.query.get(user_id)
    if request.method == 'GET':
        if not user:
            abort(400, description=f"User [{user_id}] does not exit")
            return f'User {user_id} does not exist\n', 400
        return jsonify({'username': user.username}), 200
    elif request.method == 'DELETE':
        if not User.query.get(user_id):
            abort(400, description=f'User [{user_id}] does not exit')
        db.session.delete(user)
        db.session.commit()
        return f'deleted user [{user.username}]\n', 200
    elif request.method == 'PUT':
        username = request.json.get('username')
        password = request.json.get('password')
        # there should only ever be 1 user with a given username
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is not None and existing_user.user_id != user_id:
            abort(400, description=f'User [{username}] already exists')
        user.username = username
        user.hash_password(password)
        db.session.commit()
        return (
            jsonify({'username': user.username}),
            200, 
            {'location': url_for(
                'get_all_users',
                id=user.id,
                _external=True
            )}
        )

# access resouce example
# @app.route('/api/resource')
# @auth.login_required
# def get_resource():
#     return jsonify({'data': f'Hello {g.user.username}'})

if __name__ == '__main__':
    if not os.path.exists('databases/db.sqlite'):
        db.create_all()
        app.run(debug=True)

