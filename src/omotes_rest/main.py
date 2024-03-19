import json
from time import strftime

from flask import request, send_from_directory
from werkzeug.exceptions import HTTPException

from omotes_rest import create_app
from omotes_rest.settings import EnvSettings
from omotes_rest.log import get_logger
from omotes_sdk.workflow_type import WorkflowTypeManager, WorkflowType


logger = get_logger("omotes_rest")

app = create_app("src.omotes_rest.settings.%sConfig" % EnvSettings.env().capitalize())


@app.before_request
def before_request():
    timestamp = strftime("[%Y-%b-%d %H:%M]")
    logger.debug(
        "Request",
        timestamp=timestamp,
        remote_addr=request.remote_addr,
        method=request.method,
        scheme=request.scheme,
        full_path=request.full_path,
        payload=request.get_data(),
        headers=request.headers,
    )
    # return response


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


def main() -> None:
    workflow_type_manager = WorkflowTypeManager(
        possible_workflows=[
            WorkflowType(
                workflow_type_name="grow_optimizer", workflow_type_description_name="Grow Optimizer"
            ),
            WorkflowType(
                workflow_type_name="grow_simulator", workflow_type_description_name="Grow Simulator"
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
    app.workflow_type_manager = workflow_type_manager

    app.run(
        host=EnvSettings.flask_server_host(),
        port=EnvSettings.flask_server_port(),
        use_reloader=not EnvSettings.is_production(),
    )


if __name__ == "__main__":
    main()
