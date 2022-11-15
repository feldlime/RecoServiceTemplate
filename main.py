import os

import uvicorn

from service.api.app import create_app
from service.settings import get_config

config = get_config()
app = create_app(config)


if __name__ == "__main__":

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8080"))

    uvicorn.run(app, host=host, port=port)
