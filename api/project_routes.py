from flask import Blueprint, request, jsonify
import services.project_service as project_service
from decorators import require_auth

project_bp = Blueprint("projects", __name__)

@project_bp.route("/projects", methods=["GET"])
@require_auth
def get_projects():
    """
    Get all user projects or create a new project
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - name: some_query_param
        in: query
        type: string
        required: false
        description: Filter projects by name
    responses:
      200:
        description: A list of projects
      201:
        description: Project created
      401:
        description: Unauthorized
    """
    # GET request
    projects = project_service.get_user_projects(request.user_id)
    return jsonify(projects), 200

@project_bp.route("/projects", methods=["POST"])
@require_auth
def create_project():
    """
    Get all user projects or create a new project
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      200:
        description: A list of projects
      201:
        description: Project created
      401:
        description: Unauthorized
    """
    data = request.json or {}
    slug = data.get("slug")
    name = data.get("name")
    description = data.get("description", "")
    if not slug or not name:
        return jsonify({"error": "slug and name required"}), 400
    success, message, result = project_service.create_new_project(slug, name, description, request.user_id)
    if not success:
        return jsonify({"error": message}), 400
    return jsonify(result), 201

@project_bp.route("/projects/<slug>", methods=["GET"])
@require_auth
def get_project(slug):
    """
    Get project details by slug
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - name: slug
        in: path
        type: string
        required: true
        description: The project slug
    responses:
      200:
        description: A project
      401:
        description: Unauthorized
      404:
        description: Project not found
    """
    success, message, data = project_service.get_project_details(slug)
    if not success:
        return jsonify({"error": message}), 404
    return jsonify(data)

@project_bp.route("/projects/<slug>/join", methods=["POST"])
@require_auth
def join_project(slug):
	auth_header = request.headers.get("Authorization", "")
	if not auth_header.startswith("Bearer "):
		return jsonify({"error": "Missing or invalid Authorization header"}), 401
	token = auth_header.split(" ", 1)[1]
	status, resp = auth_service.validate_token(token)
	if status != 200 or not resp.get("valid"):
		return jsonify({"error": "Invalid or expired token"}), 401
	user_id = resp.get("user_id")

	success, message, data = project_service.join_project(slug, user_id)
	if not success:
		status_code = 404 if message == "Project not found" else 400
		return jsonify({"error": message}), status_code
	response = {"message": message}
	if data:
		response.update(data)
	return jsonify(response), 200


@project_bp.route("/projects/<slug>/leave", methods=["POST"])
def leave_project(slug):
	auth_header = request.headers.get("Authorization", "")
	if not auth_header.startswith("Bearer "):
		return jsonify({"error": "Missing or invalid Authorization header"}), 401
	token = auth_header.split(" ", 1)[1]
	status, resp = auth_service.validate_token(token)
	if status != 200 or not resp.get("valid"):
		return jsonify({"error": "Invalid or expired token"}), 401
	user_id = resp.get("user_id")

	success, message, data = project_service.leave_project(slug, user_id)
	if not success:
		status_code = 404 if message == "Project not found" else 400
		return jsonify({"error": message}), status_code
	response = {"message": message}
	if data:
		response.update(data)
	return jsonify(response), 200


@project_bp.route("/projects/<slug>/membership", methods=["GET"])
def check_project_membership(slug):
	auth_header = request.headers.get("Authorization", "")
	if not auth_header.startswith("Bearer "):
		return jsonify({"error": "Missing or invalid Authorization header"}), 401
	token = auth_header.split(" ", 1)[1]
	status, resp = auth_service.validate_token(token)
	if status != 200 or not resp.get("valid"):
		return jsonify({"error": "Invalid or expired token"}), 401
	user_id = resp.get("user_id")

	success, message, data = project_service.check_user_in_project(slug, user_id)
	if not success:
		status_code = 404 if message == "Project not found" else 400
		return jsonify({"error": message}), status_code

	response = {"message": message}
	if data:
		response.update(data)
	return jsonify(response), 200
