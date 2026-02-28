from db import db
from bson import ObjectId


def get_user_project_ids(user_id):
    """Get all project IDs for projects the user is a member of"""
    user_projects = db.projects.find({"users": user_id})
    return [p["_id"] for p in user_projects]


def find_project_by_slug(slug):
    """Find a project by its slug"""
    return db.projects.find_one({"slug": slug})


def create_project(slug, name, description, owner_id):
    """Create a new project"""
    project = {
        "slug": slug,
        "name": name,
        "description": description,
        "owner": owner_id,
        "users": [owner_id]
    }
    result = db.projects.insert_one(project)
    return result.inserted_id


def get_user_projects(user_id):
    """Get all projects for a user with user_id lookups"""
    projects_cursor = db.projects.find({"users": user_id})
    projects = []
    for p in projects_cursor:
        projects.append({
            "id": str(p["_id"]),
            "name": p["name"],
            "slug": p["slug"],
            "owner": p["owner"],
            "users": p["users"],
            "description": p.get("description", "")
        })
    return projects


def add_user_to_project(project_id, user_id):
    """Add a user to a project"""
    db.projects.update_one(
        {"_id": project_id},
        {"$push": {"users": user_id}}
    )
