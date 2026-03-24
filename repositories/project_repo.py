from db import db
from bson import ObjectId


ALLOWED_PROJECT_STATUSES = {"todo", "in_progress", "done"}


def get_user_project_ids(user_id):
    """Get all project IDs for projects the user is a member of"""
    user_projects = db.projects.find({"users": user_id})
    return [p["_id"] for p in user_projects]


def find_project_by_slug(slug):
    """Find a project by its slug"""
    return db.projects.find_one({"slug": slug})


def find_project_by_id(project_id):
    """Find a project by its id"""
    if not ObjectId.is_valid(project_id):
        return None
    return db.projects.find_one({"_id": ObjectId(project_id)})


def create_project(slug, name, description, owner_id, status="todo"):
    """Create a new project"""
    normalized_status = status if status in ALLOWED_PROJECT_STATUSES else "todo"
    project = {
        "slug": slug,
        "name": name,
        "description": description,
        "owner": owner_id,
        "users": [owner_id],
        "status": normalized_status,
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
            "description": p.get("description", ""),
            "status": p.get("status", "todo"),
        })
    return projects


def add_user_to_project(project_id, user_id):
    """Add a user to a project"""
    db.projects.update_one(
        {"_id": project_id},
        {"$push": {"users": user_id}}
    )


def remove_user_from_project(project_id, user_id):
    """Remove a user from a project"""
    db.projects.update_one(
        {"_id": project_id},
        {"$pull": {"users": user_id}}
    )


def update_project_status(project_id, status):
    """Update project status"""
    normalized_status = status if status in ALLOWED_PROJECT_STATUSES else "todo"
    db.projects.update_one(
        {"_id": project_id},
        {"$set": {"status": normalized_status}}
    )
