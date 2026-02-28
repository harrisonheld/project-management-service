from flask import Flask, jsonify, request
import uuid

app = Flask(__name__)

# In-memory hardware list for mocking
hardware_db = [
    {"_id": str(uuid.uuid4()), "project_id": "1", "name": "Arduino Uno", "quantity": 10},
    {"_id": str(uuid.uuid4()), "project_id": "2", "name": "Raspberry Pi", "quantity": 5},
]

@app.route('/hardware', methods=['GET'])
def list_hardware():
    return jsonify(hardware_db), 200

@app.route('/hardware/<hardware_id>', methods=['GET'])
def get_hardware(hardware_id):
    for h in hardware_db:
        if h["_id"] == hardware_id:
            return jsonify(h), 200
    return jsonify({"error": "Not found"}), 404

@app.route('/hardware/checkout', methods=['POST'])
def checkout_hardware():
    data = request.json or {}
    hardware_id = data.get("hardware_id")
    quantity = int(data.get("quantity", 0))
    for h in hardware_db:
        if h["_id"] == hardware_id:
            if h["quantity"] >= quantity > 0:
                h["quantity"] -= quantity
                return jsonify({"message": "Checked out", "hardware": h}), 200
            else:
                return jsonify({"error": "Not enough quantity"}), 400
    return jsonify({"error": "Not found"}), 404

@app.route('/hardware/return', methods=['POST'])
def return_hardware():
    data = request.json or {}
    hardware_id = data.get("hardware_id")
    quantity = int(data.get("quantity", 0))
    for h in hardware_db:
        if h["_id"] == hardware_id and quantity > 0:
            h["quantity"] += quantity
            return jsonify({"message": "Returned", "hardware": h}), 200
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(port=5002, debug=True)
