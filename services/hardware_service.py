import os
import requests

HARDWARE_SERVICE_URL = os.environ.get("HARDWARE_SERVICE_URL")

def list_hardware():
    resp = requests.get(f"{HARDWARE_SERVICE_URL}")
    return resp.status_code, resp.json()

def get_hardware(hardware_id):
    resp = requests.get(f"{HARDWARE_SERVICE_URL}/{hardware_id}")
    return resp.status_code, resp.json()

def checkout_hardware(user_id, hardware_id, quantity):
    resp = requests.post(f"{HARDWARE_SERVICE_URL}/checkout", json={"user_id": user_id, "hardware_id": hardware_id, "quantity": quantity})
    return resp.status_code, resp.json()

def return_hardware(user_id, hardware_id, quantity):
    resp = requests.post(f"{HARDWARE_SERVICE_URL}/return", json={"user_id": user_id, "hardware_id": hardware_id, "quantity": quantity})
    return resp.status_code, resp.json()
