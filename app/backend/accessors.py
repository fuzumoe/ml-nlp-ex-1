import logging

import pymongo

from app.backend.config import get_config_variables

LOG = logging.getLogger(__name__)
CONFIG = get_config_variables()

MONGO_CLIENT_CACHE: dict[str, pymongo.MongoClient] = {}

COLLECTION_NAME = "chat_with_doc"


def get_client() -> pymongo.MongoClient:
    """Get a MongoDB client as a singleton."""
    cache_key = "default"
    if cache_key in MONGO_CLIENT_CACHE:
        return MONGO_CLIENT_CACHE[cache_key]

    client: pymongo.MongoClient = pymongo.MongoClient(CONFIG.MONGO_URL, uuidRepresentation="standard")
    MONGO_CLIENT_CACHE[cache_key] = client
    return client


def get_collection():
    from app.backend.config import get_config_variables

    config = get_config_variables()
    client = get_client()
    db = client[config.MONGO_DB_NAME]

    if COLLECTION_NAME not in db.list_collection_names():
        db.create_collection(COLLECTION_NAME)

    return db[COLLECTION_NAME]
