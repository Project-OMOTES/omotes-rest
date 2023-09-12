import os
import secrets
from pathlib import Path

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

    @staticmethod
    def postgis_host() -> str:
        return os.getenv("POSTGIS_HOST", "localhost")

    @staticmethod
    def postgis_port() -> int:
        return int(os.getenv("POSTGIS_PORT", "9232"))

    @staticmethod
    def postgis_database_name() -> str:
        return os.getenv("POSTGIS_DATABASE_NAME", "NieuweWarmteNu")

    @staticmethod
    def postgis_user() -> str:
        return os.getenv("POSTGIS_ROOT_USER", "root")

    @staticmethod
    def postgis_password() -> str:
        return os.getenv("POSTGIS_ROOT_PASSWORD", "1234")

    @staticmethod
    def nwn_postgres_host() -> str:
        return os.getenv("NWN_POSTGRES_HOST", "localhost")

    @staticmethod
    def nwn_postgres_port() -> int:
        return int(os.getenv("NWN_POSTGRES_PORT", "6432"))

    @staticmethod
    def nwn_postgres_database_name() -> str:
        return os.getenv("NWN_POSTGRES_DATABASE_NAME", "nieuwewarmtenu")

    @staticmethod
    def nwn_postgres_user() -> str:
        return os.getenv("NWN_POSTGRES_ROOT_USER", "root")

    @staticmethod
    def nwn_postgres_password() -> str:
        return os.getenv("NWN_POSTGRES_ROOT_PASSWORD", "1234")

    @staticmethod
    def nwn_rabbitmq_host() -> str:
        return os.getenv("NWN_RABBITMQ_HOST", "localhost")

    @staticmethod
    def nwn_rabbitmq_port() -> int:
        return int(os.getenv("NWN_RABBITMQ_PORT", "5672"))

    @staticmethod
    def nwn_rabbitmq_exchange() -> str:
        return os.getenv("NWN_RABBITMQ_EXCHANGE", "nwn")

    @staticmethod
    def nwn_rabbitmq_user() -> str:
        return os.getenv("NWN_RABBITMQ_ROOT_USER", "root")

    @staticmethod
    def nwn_rabbitmq_password() -> str:
        return os.getenv("NWN_RABBITMQ_ROOT_PASSWORD", "5678")

    @staticmethod
    def nwn_rabbitmq_hipe_compile() -> int:
        return int(os.getenv("NWN_RABBITMQ_HIPE_COMPILE", "1"))


class Config(object):
    """Generic config for all environments."""

    SECRET_KEY = secrets.token_urlsafe(16)

    API_TITLE = "MapEditor NWN Dispatcher REST API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/openapi"
    OPENAPI_SWAGGER_UI_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.3.2/"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_URL = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"

    API_SPEC_OPTIONS = {
        "info": {
            "description": "This is the TNO MapEditor NWN dispatcher service API.",
            "termsOfService": "https://www.tno.nl",
            "contact": {"email": "ewoud.werkman@tno.nl"},
            # "license": {"name": "TBD", "url": "https://www.tno.nl"},
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
