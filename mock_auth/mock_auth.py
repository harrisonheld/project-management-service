from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# In-memory user store for mock
users = {}

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password or username in users:
        return jsonify({'error': 'Invalid input or user exists'}), 400
    user_id = str(uuid.uuid4())
    users[username] = {'username': username, 'password': password, 'user_id': user_id}
    return jsonify({'user_id': user_id})

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = users.get(username)
    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    fake_jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mockpayload.signature'
    return jsonify({'access_token': fake_jwt, 'expires_in': 3600, 'user_id': user['user_id']})

@app.route('/auth/validate', methods=['POST'])
def validate():
    data = request.json
    token = data.get('access_token')
    # Accept only the mock token for testing
    if token and token.startswith('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'):
        # Return the first user for simplicity
        for username, info in users.items():
            return jsonify({'valid': True, 'user_id': info['user_id'], 'username': username})
    return jsonify({'valid': False}), 401

if __name__ == '__main__':
    app.run(port=5001, debug=True)
