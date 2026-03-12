
from repositories.project_repo import find_project_by_slug, find_project_by_id, create_project, get_user_projects as repo_get_user_projects, add_user_to_project, remove_user_from_project


def create_new_project(slug, name, description, user_id):
    """
    Create a new project
    Returns: (success: bool, message: str, data: dict or None)
    """
    if find_project_by_slug(slug):
        return False, "Slug already exists", None
    project_id = create_project(slug, name, description, user_id)
    return True, "Project created", {"project_id": str(project_id)}


def get_user_projects(user_id):
    """Get all projects for a user"""
    return repo_get_user_projects(user_id)


def get_project_details(slug):
    """
    Get project details
    Returns: (success: bool, message: str, data: dict or None)
    """
    project = find_project_by_slug(slug)
    if not project:
        return False, "Not found", None
    project_id = project["_id"]
    project["_id"] = str(project_id)
    project["owner"] = str(project["owner"])
    project["users"] = [str(u) for u in project["users"]]
    return True, "Project found", project


def join_project(slug, user_id):
    """
    Add a user to a project
    Returns: (success: bool, message: str, data: dict or None)
    """
    project = find_project_by_slug(slug)
    if not project:
        return False, "Project not found", None
    if user_id in project["users"]:
        return False, "Already a member of this project", None
    add_user_to_project(project["_id"], user_id)
    return True, "Successfully joined project", {
        "project_id": str(project["_id"]),
        "slug": project["slug"],
        "name": project["name"]
    }


def leave_project(slug, user_id):
    """
    Remove a user from a project
    Returns: (success: bool, message: str, data: dict or None)
    """
    project = find_project_by_slug(slug)
    if not project:
        return False, "Project not found", None

    if user_id not in project["users"]:
        return False, "Not a member of this project", None

    if len(project["users"]) <= 1:
        return False, "The last user cannot leave the project", None

    remove_user_from_project(project["_id"], user_id)
    return True, "Successfully left project", {
        "project_id": str(project["_id"]),
        "slug": project["slug"],
        "name": project["name"]
    }


def check_user_in_project(slug, user_id):
    """
    Check whether a user is a member of a project
    Returns: (success: bool, message: str, data: dict or None)
    """
    project = find_project_by_slug(slug)
    if not project:
        return False, "Project not found", None

    in_project = user_id in project["users"]
    return True, "Membership checked", {
        "project_slug": project["slug"],
        "user_id": user_id,
        "in_project": in_project,
    }


def validate_project(project_id):
    """
    Validate whether a project exists by project id
    Returns: (success: bool, message: str, data: dict)
    """
    project = find_project_by_id(project_id)
    return True, "Validation checked", {"valid": bool(project)}
