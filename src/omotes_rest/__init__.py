import logging

from flask import Flask
from flask_cors import CORS
from flask_dotenv import DotEnv
from flask_smorest import Api
from werkzeug.middleware.proxy_fix import ProxyFix

from dotenv import load_dotenv

from omotes_rest.rest_interface import RestInterface

load_dotenv(verbose=True)

import os  # noqa: E402
from omotes_sdk.internal.common.app_logging import setup_logging, LogLevel  # noqa: E402

setup_logging(LogLevel.parse(os.environ.get("LOG_LEVEL", "INFO")), "omotes_rest")
setup_logging(LogLevel.parse(os.environ.get("LOG_LEVEL_SQL", "WARNING")), "sqlalchemy.engine")

api = Api()
env = DotEnv()


def create_app(object_name: str) -> Flask:
    """Create Flask app.

    A flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    :param object_name: the python path of the config object, e.g.
        influxdbgraphs.api.settings.ProdConfig
    :return: The initalised Flask app.
    """
    logger = logging.getLogger("omotes_rest")
    logger.info("Setting up app.")

    app = Flask(__name__)
    app.config.from_object(object_name)
    app.wsgi_app = ProxyFix(app.wsgi_app)  # type: ignore[method-assign]

    env.init_app(app)
    api.init_app(app)

    # Register blueprints.
    from omotes_rest.apis.job import api as job_api

    api.register_blueprint(job_api)

    CORS(app, resources={r"/*": {"origins": "*"}})

    logger.info("Finished setting up app.")

    return app
