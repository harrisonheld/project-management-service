import logging
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

logger = logging.getLogger(__name__)

# MongoDB setup
uri = os.environ.get("MONGO_URI")
if not uri:
    raise ValueError("MONGO_URI environment variable not set")
client = MongoClient(uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)
db = client["project_management"]
logger.info("MongoDB connected to project_management database")
