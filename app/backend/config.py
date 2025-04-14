import logging
import os

from dotenv import load_dotenv

LOG = logging.getLogger(__name__)


class Config:
    def __init__(self) -> "None":
        load_dotenv()
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
        self.S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
        self.MONGO_URL = os.getenv("MONGO_URL")
        self.MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

        for var in [
            self.OPENAI_API_KEY,
            self.MONGO_URL,
            self.OPENAI_API_BASE,
            self.OPENAI_API_BASE,
            self.MONGO_DB_NAME,
        ]:
            if var is None:
                LOG.error(f"Environment variable {var} is not set.")
                msg = f"Environment variable {var} is not set."
                raise ValueError(msg)

        os.environ["OPENAI_API_KEY"] = self.OPENAI_API_KEY or ""
        os.environ["OPENAI_API_BASE"] = self.OPENAI_API_BASE or ""


def get_config_variables() -> Config:
    """Get configuration variables.

    Returns:
        Config: The configuration object containing all variables.

    Raises:
        ValueError: if any environment variable is not set.

    """
    config = Config()
    LOG.info("Configuration variables loaded successfully.")
    return config
