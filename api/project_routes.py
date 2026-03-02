from flask import Blueprint, request, jsonify
<<<<<<< HEAD
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity
=======
>>>>>>> 3ee7691 (wip)
from services.project_service import (
	create_new_project,
	get_user_projects as get_user_projects_service,
	get_project_details,
	join_project as join_project_service
)
from services.auth_service import validate_token

project_bp = Blueprint("projects", __name__)


@project_bp.route("/projects", methods=["GET", "POST"])
def projects():
<<<<<<< HEAD
	"""
	Get all user projects or create a new project
	---
    responses:
      200:
        description: A list of projects
	"""
	user_id = get_jwt_identity()
    
=======
	"""Get all user projects or create a new project"""
	auth_header = request.headers.get("Authorization", "")
	if not auth_header.startswith("Bearer "):
		return jsonify({"error": "Missing or invalid Authorization header"}), 401
	token = auth_header.split(" ", 1)[1]
	status, resp = validate_token(token)
	if status != 200 or not resp.get("valid"):
		return jsonify({"error": "Invalid or expired token"}), 401
	user_id = resp.get("username")

>>>>>>> 3ee7691 (wip)
	if request.method == "POST":
		data = request.json or {}
		slug = data.get("slug")
		name = data.get("name")
		description = data.get("description", "")

		if not slug or not name:
			return jsonify({"error": "slug and name required"}), 400

		success, message, result = create_new_project(slug, name, description, user_id)
		if not success:
			return jsonify({"error": message}), 400
		return jsonify(result), 201

	# GET request
	projects = get_user_projects_service(user_id)
	return jsonify(projects), 200


@project_bp.route("/projects/<slug>", methods=["GET"])
def get_project(slug):
<<<<<<< HEAD
	"""
	Get project details by slug
	---
    responses:
      200:
        description: A project
	"""
=======
	auth_header = request.headers.get("Authorization", "")
	if not auth_header.startswith("Bearer "):
		return jsonify({"error": "Missing or invalid Authorization header"}), 401
	token = auth_header.split(" ", 1)[1]
	status, resp = validate_token(token)
	if status != 200 or not resp.get("valid"):
		return jsonify({"error": "Invalid or expired token"}), 401

>>>>>>> 3ee7691 (wip)
	success, message, data = get_project_details(slug)
	if not success:
		return jsonify({"error": message}), 404
	return jsonify(data)


@project_bp.route("/projects/<slug>/join", methods=["POST"])
def join_project(slug):
<<<<<<< HEAD
	"""
	Join a project by slug
	---
    responses:
      200:
        description: add a user to a project
	"""
	user_id = get_jwt_identity()
=======
	auth_header = request.headers.get("Authorization", "")
	if not auth_header.startswith("Bearer "):
		return jsonify({"error": "Missing or invalid Authorization header"}), 401
	token = auth_header.split(" ", 1)[1]
	status, resp = validate_token(token)
	if status != 200 or not resp.get("valid"):
		return jsonify({"error": "Invalid or expired token"}), 401
	user_id = resp.get("username")

>>>>>>> 3ee7691 (wip)
	success, message, data = join_project_service(slug, user_id)
	if not success:
		status_code = 404 if message == "Project not found" else 400
		return jsonify({"error": message}), status_code
	return jsonify({"message": message, **data}), 200
