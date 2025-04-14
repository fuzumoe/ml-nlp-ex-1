import logging
from typing import Any

import pymongo

from app.backend.config import get_config_variables

LOG = logging.getLogger(__name__)
CONFIG = get_config_variables()

MONGO_CLIENT_CACHE: dict[str, pymongo.MongoClient[dict[str, Any]]] = {}
COLLECTION_NAME = "chat_with_doc"


def get_client() -> pymongo.MongoClient[dict[str, Any]]:
    """Get the MongoDB client.

        This function caches the MongoDB client to avoid creating a new connection
        for every request. The cache is stored in the MONGO_CLIENT_CACHE dictionary.
        The cache key is set to "default" for simplicity.
        If you need to support multiple clients, you can modify the cache key
        to be unique for each client.

    Args:
        None
    Returns:
        pymongo.MongoClient: The MongoDB client.

    Raises:
        pymongo.errors.ConnectionError: If the connection to MongoDB fails.

    """
    cache_key = "default"
    if cache_key in MONGO_CLIENT_CACHE:
        return MONGO_CLIENT_CACHE[cache_key]

    try:
        client: pymongo.MongoClient[dict[str, Any]] = pymongo.MongoClient(
            CONFIG.MONGO_URL, uuidRepresentation="standard"
        )
    except ConnectionError as e:
        message = str(e)
        LOG.exception(f"Failed to connect to MongoDB: {message}")
        raise
    MONGO_CLIENT_CACHE[cache_key] = client
    return client


def get_collection() -> Any:
    """Get the MongoDB collection.

    This function retrieves the MongoDB collection for storing chat history.
    It creates the collection if it does not exist.

    Args:
        None
    Returns:
        pymongo.collection.Collection: The MongoDB collection for chat history.

    """
    client = get_client()
    db_name = CONFIG.MONGO_DB_NAME or "default_db"  # Ensure db_name is a string
    db = client[db_name]

    if COLLECTION_NAME not in db.list_collection_names():
        db.create_collection(COLLECTION_NAME)

    return db[COLLECTION_NAME]
