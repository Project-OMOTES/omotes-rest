import os
import secrets

from dotenv import load_dotenv

load_dotenv(verbose=True)


class EnvSettings:
    @staticmethod
    def env() -> str:
        return os.getenv("ENV", "dev")

    @staticmethod
    def flask_server_host() -> str:
        return "0.0.0.0"

    @staticmethod
    def flask_server_port() -> int:
        return 9200

    @staticmethod
    def is_production():
        return EnvSettings.env() == "prod"



class Config(object):
    """Generic config for all environments."""

    SECRET_KEY = secrets.token_urlsafe(16)

    API_TITLE = "MapEditor Optimizer Dispatcher REST API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/openapi"
    OPENAPI_SWAGGER_UI_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.3.2/"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_URL = (
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )

    API_SPEC_OPTIONS = {
        "info": {
            "description": "This is the TNO NWN MapEditor Optimizer dispatcher service API.",
            "termsOfService": "https://www.tno.nl",
            "contact": {"email": "ewoud.werkman@tno.nl"},
            #"license": {"name": "TBD", "url": "https://www.tno.nl"},
        }
    }


class ProdConfig(Config):
    ENV = "prod"
    DEBUG = False
    FLASK_DEBUG = False


class DevConfig(Config):
    ENV = "dev"
    DEBUG = True
    FLASK_DEBUG = True
