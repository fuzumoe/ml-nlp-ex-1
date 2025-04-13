import logging

import pymongo

from app.backend.config import get_config_variables

LOG = logging.getLogger(__name__)
CONFIG = get_config_variables()

_mongo_client_cache: dict[str, pymongo.MongoClient] = {}

_collection_name = "chat_with_doc"
_db_name = get_config_variables().MONGO_DB_NAME  # ✅ Ensure this is in your config class/env


def get_client() -> pymongo.MongoClient:
    """Get a MongoDB client as a singleton."""
    cache_key = "default"
    if cache_key in _mongo_client_cache:
        return _mongo_client_cache[cache_key]

    client: pymongo.MongoClient = pymongo.MongoClient(CONFIG.MONGO_URL, uuidRepresentation="standard")
    _mongo_client_cache[cache_key] = client
    return client


def get_collection():
    from app.backend.config import get_config_variables

    config = get_config_variables()
    client = get_client()
    db = client[config.MONGO_DB_NAME]

    if _collection_name not in db.list_collection_names():
        db.create_collection(_collection_name)

    return db[_collection_name]
