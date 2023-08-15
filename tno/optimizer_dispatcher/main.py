import json
from time import strftime

from flask import request, send_from_directory
from tno.optimizer_dispatcher import create_app
from tno.optimizer_dispatcher.settings import EnvSettings

from tno.shared.log import get_logger
from werkzeug.exceptions import HTTPException

# Convert warnings into exceptions
# import sys

# if not sys.warnoptions:
#     import warnings

# warnings.filterwarnings("error")


logger = get_logger("tno.optimizer_dispatcher.main")

app = create_app("tno.optimizer_dispatcher.settings.%sConfig" % EnvSettings.env().capitalize())

@app.after_request
def after_request(response):
    timestamp = strftime("[%Y-%b-%d %H:%M]")
    logger.debug(
        "Request",
        timestamp=timestamp,
        remote_addr=request.remote_addr,
        method=request.method,
        scheme=request.scheme,
        full_path=request.full_path,
        response=response.status,
    )
    return response


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    response.data = json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response


@app.errorhandler(Exception)
def handle_500(e):
    logger.exception("Unhandled exception occurred", message=str(e))
    return json.dumps({"message": "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(
        host=EnvSettings.flask_server_host(),
        port=EnvSettings.flask_server_port(),
        use_reloader=not EnvSettings.is_production(),
    )
