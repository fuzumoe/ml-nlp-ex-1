from pydantic import BaseModel
import pymongo

import traceback

import os, sys

from fastapi import (
    FastAPI,
    UploadFile,
    status,
    HTTPException,
)
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from langchain.text_splitter import RecursiveCharacterTextSplitter