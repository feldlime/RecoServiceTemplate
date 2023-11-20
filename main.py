import os
import random

from pydantic import BaseModel
import uvicorn
from typing import Union, List
from fastapi import FastAPI
from service.api.app import create_app
from service.settings import get_config

config = get_config()
app = create_app(config)


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8081"))

    uvicorn.run(app, host=host, port=port)
