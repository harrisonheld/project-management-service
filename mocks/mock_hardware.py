from flask import Flask, jsonify, request
import random


app = Flask(__name__)


# Helper to generate a random 24-character hex string (MongoDB ObjectId style)
def random_objectid():
    return ''.join(random.choices('0123456789abcdef', k=24))

# In-memory hardware list for mocking
hardware_db = [
    {
        "hardware_id": random_objectid(),
        "name": "Arduino Uno",
        "description": "Microcontroller board",
        "quantity": 10,
        "capacity": 100
    },
    {
        "hardware_id": random_objectid(),
        "name": "Raspberry Pi",
        "description": "A small computer",
        "quantity": 5,
        "capacity": 100
    }
]

@app.route('/hardware', methods=['GET'])
def list_hardware():
    return jsonify(hardware_db), 200

@app.route('/hardware/<hardware_id>', methods=['GET'])
def get_hardware(hardware_id):
    for h in hardware_db:
        if h["hardware_id"] == hardware_id:
            return jsonify(h), 200
    return jsonify({"error": "Hardware not found"}), 404

@app.route('/hardware/checkout', methods=['POST'])
def checkout_hardware():
    data = request.json or {}
    hardware_id = data.get("hardware_id")
    try:
        quantity = int(data.get("quantity", 0))
    except Exception:
        return jsonify({"error": "Invalid quantity"}), 400
    if not hardware_id:
        return jsonify({"error": "Could not find hardware with that id"}), 400
    if quantity <= 0:
        return jsonify({"error": "Invalid quantity"}), 400
    for h in hardware_db:
        if h["hardware_id"] == hardware_id:
            if h["quantity"] >= quantity:
                h["quantity"] -= quantity
                return jsonify({"success": True, "message": f"Checked out {quantity} {h['name']}"}), 200
            else:
                return jsonify({"error": "Not enough hardware available"}), 400
    return jsonify({"error": "Hardware not found"}), 404

@app.route('/hardware/return', methods=['POST'])
def return_hardware():
    data = request.json or {}
    hardware_id = data.get("hardware_id")
    quantity = int(data.get("quantity", 0))
    if not hardware_id or quantity <= 0:
        return jsonify({"error": "Invalid input"}), 400
    for h in hardware_db:
        if h["hardware_id"] == hardware_id:
            h["quantity"] += quantity
            return jsonify({"success": True, "message": f"Returned {quantity} {h['name']}"}), 200
    return jsonify({"error": "Hardware not found"}), 404

if __name__ == '__main__':
    app.run(port=5002, debug=True)
