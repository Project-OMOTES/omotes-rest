import logging

from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify, Response

from omotes_rest.typed_app import current_app


logger = logging.getLogger("omotes_rest")

api = Blueprint(
    "Workflow",
    "Workflow",
    url_prefix="/workflow",
    description="Omotes workflows: retrieve the available workflow and their properties",
)


@api.route("/")
class JobAPI(MethodView):
    """Requests."""

    def get(self) -> Response:
        """Return a summary of all workflows with parameter jsonforms format."""
        return jsonify(current_app.rest_if.get_workflows_jsonforms_format())
