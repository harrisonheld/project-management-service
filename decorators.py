from functools import wraps
from flask import request, jsonify
import services.auth_service as auth_service

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ", 1)[1]
        status, resp = auth_service.validate_token(token)
        if status != 200 or not resp.get("valid"):
            return jsonify({"error": "Invalid or expired token"}), 401
        request.user_id = resp.get("user_id")
        return f(*args, **kwargs)
    return decorated