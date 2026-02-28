from flask import Blueprint, request, jsonify
import services.project_service as project_service
import services.auth_service as auth_service

project_bp = Blueprint("projects", __name__)


@project_bp.route("/projects", methods=["GET", "POST"])
def projects():
	"""Get all user projects or create a new project"""
	auth_header = request.headers.get("Authorization", "")
	if not auth_header.startswith("Bearer "):
		return jsonify({"error": "Missing or invalid Authorization header"}), 401
	token = auth_header.split(" ", 1)[1]
	status, resp = auth_service.validate_token(token)
	if status != 200 or not resp.get("valid"):
		return jsonify({"error": "Invalid or expired token"}), 401
	user_id = resp.get("username")

	if request.method == "POST":
		data = request.json or {}
		slug = data.get("slug")
		name = data.get("name")
		description = data.get("description", "")

		if not slug or not name:
			return jsonify({"error": "slug and name required"}), 400

		success, message, result = project_service.create_new_project(slug, name, description, user_id)
		if not success:
			return jsonify({"error": message}), 400
		return jsonify(result), 201

	# GET request
	projects = project_service.get_user_projects(user_id)
	return jsonify(projects), 200


@project_bp.route("/projects/<slug>", methods=["GET"])
def get_project(slug):
	auth_header = request.headers.get("Authorization", "")
	if not auth_header.startswith("Bearer "):
		return jsonify({"error": "Missing or invalid Authorization header"}), 401
	token = auth_header.split(" ", 1)[1]
	status, resp = auth_service.validate_token(token)
	if status != 200 or not resp.get("valid"):
		return jsonify({"error": "Invalid or expired token"}), 401

	success, message, data = project_service.get_project_details(slug)
	if not success:
		return jsonify({"error": message}), 404
	return jsonify(data)


@project_bp.route("/projects/<slug>/join", methods=["POST"])
def join_project(slug):
	auth_header = request.headers.get("Authorization", "")
	if not auth_header.startswith("Bearer "):
		return jsonify({"error": "Missing or invalid Authorization header"}), 401
	token = auth_header.split(" ", 1)[1]
	status, resp = auth_service.validate_token(token)
	if status != 200 or not resp.get("valid"):
		return jsonify({"error": "Invalid or expired token"}), 401
	user_id = resp.get("username")

	success, message, data = project_service.join_project(slug, user_id)
	if not success:
		status_code = 404 if message == "Project not found" else 400
		return jsonify({"error": message}), status_code
	return jsonify({"message": message, **data}), 200
