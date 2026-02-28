from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# In-memory hardware store
hardware_db = {
    "1": {"hardware_id": "1", "name": "Raspberry Pi", "description": "A small computer", "quantity": 10},
    "2": {"hardware_id": "2", "name": "Arduino Uno", "description": "Microcontroller board", "quantity": 5}
}

@app.route('/hardware', methods=['GET'])
def list_hardware():
    return jsonify(list(hardware_db.values()))

@app.route('/hardware/<hardware_id>', methods=['GET'])
def get_hardware(hardware_id):
    hw = hardware_db.get(hardware_id)
    if not hw:
        return jsonify({"error": "Not found"}), 404
    return jsonify(hw)

@app.route('/hardware/checkout', methods=['POST'])
def checkout_hardware():
    data = request.json
    hardware_id = data.get('hardware_id')
    quantity = int(data.get('quantity', 0))
    hw = hardware_db.get(hardware_id)
    if not hw or quantity <= 0 or hw['quantity'] < quantity:
        return jsonify({"success": False, "message": "Not enough hardware available"}), 400
    hw['quantity'] -= quantity
    return jsonify({"success": True, "message": f"Checked out {quantity} {hw['name']}"})

@app.route('/hardware/return', methods=['POST'])
def return_hardware():
    data = request.json
    hardware_id = data.get('hardware_id')
    quantity = int(data.get('quantity', 0))
    hw = hardware_db.get(hardware_id)
    if not hw or quantity <= 0:
        return jsonify({"success": False, "message": "Invalid return"}), 400
    hw['quantity'] += quantity
    return jsonify({"success": True, "message": f"Returned {quantity} {hw['name']}"})

if __name__ == '__main__':
    app.run(port=5002, debug=True)
