import json
from time import strftime

from flask import request, send_from_directory, current_app
from werkzeug.exceptions import HTTPException

from omotes_rest import create_app
from omotes_rest.rest_interface import RestInterface
from omotes_rest.settings import EnvSettings
import logging
from omotes_sdk.workflow_type import WorkflowTypeManager, WorkflowType

"""logger."""
logger = logging.getLogger("omotes_rest")

"""Flask application."""
app = create_app("omotes_rest.settings.%sConfig" % EnvSettings.env().capitalize())


@app.before_request
def before_request():
    """Log before request."""
    timestamp = strftime("[%Y-%b-%d %H:%M]")
    logger.debug(
        f"Request, timestamp '{timestamp}', remote_addr '{request.remote_addr}',"
        f" method '{request.method}', scheme '{request.scheme}', full_path '{request.full_path},"
        f" 'payload '{request.get_data()}', 'headers '{request.headers}'")
    # return response


@app.after_request
def after_request(response):
    """Log after request."""
    timestamp = strftime("[%Y-%b-%d %H:%M]")
    logger.debug(
        f"Request, timestamp '{timestamp}', remote_addr '{request.remote_addr}',"
        f" method '{request.method}', scheme '{request.scheme}', full_path '{request.full_path},"
        f" 'response '{response.status}'")
    return response


@app.route("/<path:path>")
def serve_static(path):
    """Serve static."""
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
    """Handle exceptions."""
    logger.exception(f"Unhandled exception occurred {str(e)}")
    return json.dumps({"message": "Internal Server Error"}), 500


# TODO to be retrieved via de omotes_sdk in the future
workflow_type_manager = WorkflowTypeManager(
    possible_workflows=[
        WorkflowType(
            workflow_type_name="grow_optimizer",
            workflow_type_description_name="Grow Optimizer"
        ),
        WorkflowType(
            workflow_type_name="grow_simulator",
            workflow_type_description_name="Grow Simulator"
        ),
        WorkflowType(
            workflow_type_name="grow_optimizer_no_heat_losses",
            workflow_type_description_name="Grow Optimizer without heat losses",
        ),
        WorkflowType(
            workflow_type_name="grow_optimizer_no_heat_losses_discounted_capex",
            workflow_type_description_name="Grow Optimizer without heat losses and a "
                                           "discounted CAPEX",
        ),
        WorkflowType(
            workflow_type_name="simulator",
            workflow_type_description_name="High fidelity simulator",
        ),
    ]
)


def post_fork(_, __):
    """Called just after a worker has been forked."""
    with app.app_context():
        """current_app is only within the app context"""

        current_app.rest_if = RestInterface(workflow_type_manager)
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
