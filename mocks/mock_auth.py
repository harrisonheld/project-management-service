
from flask import Flask, request, jsonify
import jwt
import datetime
import random


app = Flask(__name__)

# JWT secret and algorithm (for mock only)
JWT_SECRET = 'mock_secret_key'
JWT_ALGORITHM = 'HS256'

# Helper to generate a random 24-character hex string (MongoDB ObjectId style)
def random_objectid():
    return ''.join(random.choices('0123456789abcdef', k=24))

# In-memory user store for mock
users = {}

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    if username in users:
        return jsonify({'error': 'Username already registered'}), 400
    user_id = random_objectid()
    users[username] = {'username': username, 'password': password, 'user_id': user_id}
    return jsonify({'user_id': user_id})

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = users.get(username)
    if not user:
        return jsonify({'error': 'User does not exist'}), 401
    if user['password'] != password:
        return jsonify({'error': 'Password does not match'}), 401
    payload = {
        'user_id': user['user_id'],
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return jsonify({'access_token': token, 'expires_in': 3600, 'user_id': user['user_id']})

@app.route('/auth/validate', methods=['POST'])
def validate():
    data = request.json
    token = data.get('access_token')
    if not token:
        return jsonify({'valid': False, 'reason': 'Missing token'}), 401
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        username = payload.get('username')
        # Check user exists in our in-memory store
        user = users.get(username)
        if not user or user['user_id'] != user_id:
            return jsonify({'valid': False, 'reason': 'User not found'}), 401
        return jsonify({'valid': True, 'user_id': user_id, 'username': username})
    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'reason': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'reason': 'Invalid token'}), 401

if __name__ == '__main__':
    app.run(port=5001, debug=True)
