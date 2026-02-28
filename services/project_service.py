from repositories.project_repo import (
    find_project_by_slug,
    create_project as create_project_repo,
    get_user_projects as get_user_projects_repo,
    add_user_to_project as add_user_repo
)
from bson import ObjectId


def create_new_project(slug, name, description, user_id):
    """
    Create a new project
    Returns: (success: bool, message: str, data: dict or None)
    """
    if find_project_by_slug(slug):
        return False, "Slug already exists", None
    
    project_id = create_project_repo(slug, name, description, user_id)
    
    return True, "Project created", {"project_id": str(project_id)}


def get_user_projects(user_id):
    """Get all projects for a user"""
    return get_user_projects_repo(user_id)


def get_project_details(slug):
    """
    Get project details including hardware
    Returns: (success: bool, message: str, data: dict or None)
    """
    project = find_project_by_slug(slug)
    
    if not project:
        return False, "Not found", None
    
    project_id = project["_id"]
    project["_id"] = str(project_id)
    project["owner"] = str(project["owner"])
    project["users"] = [str(u) for u in project["users"]]
    
    from db import db
    hardware = list(db.hardware.find({"project_id": project_id}))
    for h in hardware:
        h["_id"] = str(h["_id"])
        h["project_id"] = str(h["project_id"])
    
    project["hardware"] = hardware
    return True, "Project found", project


def join_project(slug, user_id):
    """
    Add a user to a project
    Returns: (success: bool, message: str, data: dict or None)
    """
    project = find_project_by_slug(slug)
    
    if not project:
        return False, "Project not found", None
    
    user_obj_id = ObjectId(user_id)
    if user_obj_id in project["users"]:
        return False, "Already a member of this project", None
    
    add_user_repo(project["_id"], user_id)
    
    return True, "Successfully joined project", {
        "project_id": str(project["_id"]),
        "slug": project["slug"],
        "name": project["name"]
    }
