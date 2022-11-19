from service.api.app import create_app
from service.settings import get_config

config = get_config()
app = create_app(config)
