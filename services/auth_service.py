# auth_service.py:
# this service will delegate tasks to the Auth Service by sending HTTPS requests

import os
import requests

AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://localhost:5001/auth")

def register_user(username, password):
    resp = requests.post(f"{AUTH_SERVICE_URL}/register", json={"username": username, "password": password})
    return resp.status_code, resp.json()

def login_user(username, password):
    resp = requests.post(f"{AUTH_SERVICE_URL}/login", json={"username": username, "password": password})
    return resp.status_code, resp.json()

def validate_token(token):
    resp = requests.post(f"{AUTH_SERVICE_URL}/validate", json={"access_token": token})
    return resp.status_code, resp.json()
