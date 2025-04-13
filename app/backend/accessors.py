import logging
from typing import Any

import boto3
import pymongo
from botocore.client import Config

from app.backend.config import get_config_variables

LOG = logging.getLogger(__name__)
CONFIG = get_config_variables()

_mongo_client_cache: dict[str, pymongo.MongoClient] = {}
_s3_client_cache: dict[str, Any] = {}

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


def get_collection() -> Any:
    """Get the MongoDB collection. Create it if it does not exist."""
    client = get_client()
    db = client[_db_name]  # ✅ Explicit DB access

    if _collection_name not in db.list_collection_names():
        LOG.info(f"Collection '{_collection_name}' not found. Creating it.")
        db.create_collection(_collection_name)

    return db[_collection_name]


def get_s3_client() -> Any:
    """Get an S3 client as a singleton."""
    cache_key = "client"
    if cache_key in _s3_client_cache:
        return _s3_client_cache[cache_key]

    s3_client = boto3.client(
        "s3",
        endpoint_url=CONFIG.S3_URL,
        aws_access_key_id=CONFIG.S3_KEY,
        aws_secret_access_key=CONFIG.S3_SECRET,
        region_name=CONFIG.S3_REGION,
        config=Config(signature_version="s3v4"),
    )
    _s3_client_cache[cache_key] = s3_client
    return s3_client
