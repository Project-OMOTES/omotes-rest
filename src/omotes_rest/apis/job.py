import base64

from flask import current_app
from flask_smorest import Blueprint
from flask.views import MethodView

from omotes_rest.apis.api_dataclasses import (
    JobInput,
    JobResponse,
    JobStatusResponse,
    JobResultResponse,
    JobLogsResponse,
    JobSummary,
    JobDeleteResponse,
    JobCancelResponse,
)
import logging

logger = logging.getLogger("omotes_rest")

api = Blueprint(
    "Job",
    "Job",
    url_prefix="/job",
    description="Omotes jobs: start, check status and get overview and results",
)


@api.route("/")
class JobAPI(MethodView):
    """Requests."""

    @api.arguments(JobInput.Schema())
    @api.response(200, JobStatusResponse.Schema())
    def post(self, job_input: JobInput):
        """Start new job: 'input_params_dict' can have lists and (nested) dicts as values."""
        return current_app.rest_if.submit_job(job_input)

    @api.response(200, JobSummary.Schema(many=True))
    def get(self):
        """Return a summary of all jobs."""
        return current_app.rest_if.get_jobs()


@api.route("/<string:job_id>")
class JobFromIdAPI(MethodView):
    """Requests."""

    @api.response(200, JobResponse.Schema())
    def get(self, job_id: str):
        """Return job details."""
        return current_app.rest_if.get_job(job_id)

    @api.response(200, JobDeleteResponse.Schema())
    def delete(self, job_id: str):
        """Delete job, and cancel if queued or running."""
        return JobDeleteResponse(job_id=job_id, deleted=current_app.rest_if.delete_job(job_id))


@api.route("/<string:job_id>/cancel")
class JobCancelAPI(MethodView):
    """Requests."""

    @api.response(200, JobCancelResponse.Schema())
    def get(self, job_id: str):
        """Cancel job if queued or running."""
        return JobCancelResponse(job_id=job_id, cancelled=current_app.rest_if.cancel_job(job_id))


@api.route("/<string:job_id>/status")
class JobStatusAPI(MethodView):
    """Requests."""

    @api.response(200, JobStatusResponse.Schema())
    def get(self, job_id: str):
        """Return job status."""
        return JobStatusResponse(job_id=job_id, status=current_app.rest_if.get_job_status(job_id))


@api.route("/<string:job_id>/result")
class JobResultAPI(MethodView):
    """Requests."""

    @api.response(200, JobResultResponse.Schema())
    def get(self, job_id: int):
        """Return job result with output ESDL (can be None)"""
        output_esdl = current_app.rest_if.get_job_output_esdl(job_id)
        if output_esdl:
            output_esdl = base64.b64encode(bytes(output_esdl, "utf-8")).decode("utf-8")
        return JobResultResponse(job_id=job_id, output_esdl=output_esdl)


@api.route("/<string:job_id>/logs")
class JobLogsAPI(MethodView):
    """Requests."""

    @api.response(200, JobLogsResponse.Schema())
    def get(self, job_id: int):
        """Return job logs."""
        logs = current_app.rest_if.get_job_logs(job_id)
        if not logs:
            logs = "No logs received for this job."
        return JobLogsResponse(job_id=job_id, logs=logs)


@api.route("/user/<string:user_name>")
class JobsByUserAPI(MethodView):
    """Requests."""

    @api.response(200, JobSummary.Schema(many=True))
    def get(self, user_name: str):
        """Return all jobs from user."""
        return current_app.rest_if.get_jobs_from_user(user_name)


@api.route("/project/<string:project_name>")
class JobByProjectAPI(MethodView):
    """Requests."""

    @api.response(200, JobSummary.Schema(many=True))
    def get(self, project_name: str):
        """Return all jobs from project."""
        return current_app.rest_if.get_jobs_from_project(project_name)
