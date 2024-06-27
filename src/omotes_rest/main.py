import json
import logging
from os import PathLike
from time import strftime

from flask import request, send_from_directory, Response as FlaskResponse
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers.response import Response as WerkzeugResponse
from gunicorn.arbiter import Arbiter
from gunicorn.workers.sync import SyncWorker

from omotes_rest import create_app
from omotes_rest.rest_interface import RestInterface
from omotes_rest.settings import EnvSettings
from omotes_rest.typed_app import current_app


"""logger."""
logger = logging.getLogger("omotes_rest")

"""Flask application."""
app = create_app("omotes_rest.settings.%sConfig" % EnvSettings.env().capitalize())


@app.before_request
def before_request() -> None:
    """Log before request."""
    timestamp = strftime("[%Y-%b-%d %H:%M]")

    logger.debug(
        f"Request, timestamp '{timestamp}', remote_addr '{request.remote_addr}',"
        f" method '{request.method}', scheme '{request.scheme}', full_path '{request.full_path},"
        f" 'payload '{request.get_data()!r}', 'headers '{request.headers}'"
    )
    # return response


@app.after_request
def after_request(response: FlaskResponse) -> FlaskResponse:
    """Log after request."""
    timestamp = strftime("[%Y-%b-%d %H:%M]")
    logger.debug(
        f"Request, timestamp '{timestamp}', remote_addr '{request.remote_addr}',"
        f" method '{request.method}', scheme '{request.scheme}', full_path '{request.full_path},"
        f" 'response '{response.status}'"
    )
    return response


@app.route("/<path:path>")
def serve_static(path: PathLike | str) -> FlaskResponse:
    """Serve static."""
    return send_from_directory("static", path)


@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException) -> WerkzeugResponse:
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    data = json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return WerkzeugResponse(
        response=data,
        status=response.status_code,
        headers=response.headers,
        mimetype=response.mimetype,
        content_type=response.content_type,
    )


@app.errorhandler(Exception)
def handle_500(e: Exception) -> tuple[str, int]:
    """Handle exceptions."""
    logger.exception(f"Unhandled exception occurred {str(e)}")
    return json.dumps({"message": "Internal Server Error"}), 500


def post_fork(_: Arbiter, __: SyncWorker) -> None:
    """Called just after a worker has been forked."""
    with app.app_context():
        """current_app is only within the app context"""

        current_app.rest_if = RestInterface()
        """Interface for this Omotes Rest service."""

        current_app.rest_if.start()


def main() -> None:
    """Main function which creates and starts the omotes rest service.

    Waits indefinitely until the omotes rest service stops.
    """
    app.run(
        host=EnvSettings.flask_server_host(),
        port=EnvSettings.flask_server_port(),
        use_reloader=not EnvSettings.is_production(),
    )


if __name__ == "__main__":
    main()
