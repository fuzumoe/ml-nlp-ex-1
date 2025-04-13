import logging
import os

from dotenv import load_dotenv

LOG = logging.getLogger(__name__)


class Config:
    def __init__(self):
        load_dotenv()
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = self.OPENAI_API_KEY
        self.S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
        self.S3_URL = os.getenv("S3_ENDPOINT_URL")
        self.S3_KEY = os.getenv("S3_ACCESS_KEY")
        self.S3_SECRET = os.getenv("S3_SECRET_KEY")
        self.S3_BUCKET = os.getenv("S3_BUCKET")
        self.S3_REGION = os.getenv("S3_REGION")
        self.S3_PATH = os.getenv("S3_PATH")
        self.MONGO_URL = os.getenv("MONGO_URL")

        for var in [
            self.OPENAI_API_KEY,
            self.S3_ENDPOINT_URL,
            self.S3_KEY,
            self.S3_SECRET,
            self.S3_BUCKET,
            self.S3_REGION,
            self.S3_PATH,
            self.MONGO_URL,
        ]:
            if var is None:
                LOG.error(f"Environment variable {var} is not set.")
                msg = f"Environment variable {var} is not set."
                raise ValueError(msg)

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
    S3_URL = os.getenv("S3_ENDPOINT_URL")
    S3_KEY = os.getenv("S3_ACCESS_KEY")
    S3_SECRET = os.getenv("S3_SECRET_KEY")
    S3_BUCKET = os.getenv("S3_BUCKET")
    S3_REGION = os.getenv("S3_REGION")
    S3_PATH = os.getenv("S3_PATH")
    MONGO_URL = os.getenv("MONGO_URL")


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
