import base64
import logging
import uuid


from flask import Response
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
from omotes_rest.db_models.job_rest import JobRest
from omotes_rest.typed_app import current_app


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
    def post(self, job_input: JobInput) -> JobStatusResponse:
        """Start new job: 'input_params_dict' can have lists and (nested) dicts as values."""
        return current_app.rest_if.submit_job(job_input)

    @api.response(200, JobSummary.Schema(many=True))
    def get(self) -> list[JobRest]:
        """Return a summary of all jobs."""
        return current_app.rest_if.get_jobs()


@api.route("/<string:job_id>")
class JobFromIdAPI(MethodView):
    """Requests."""

    @api.response(200, JobResponse.Schema())
    def get(self, job_id: str) -> JobRest | None:
        """Return job details."""
        return current_app.rest_if.get_job(uuid.UUID(job_id))

    @api.response(200, JobDeleteResponse.Schema())
    def delete(self, job_id: str) -> JobDeleteResponse:
        """Delete job, and cancel if queued or running."""
        job_uuid = uuid.UUID(job_id)
        return JobDeleteResponse(job_id=job_uuid, deleted=current_app.rest_if.delete_job(job_uuid))


@api.route("/<string:job_id>/cancel")
class JobCancelAPI(MethodView):
    """Requests."""

    @api.response(200, JobCancelResponse.Schema())
    def get(self, job_id: str) -> JobCancelResponse:
        """Cancel job if queued or running."""
        job_uuid = uuid.UUID(job_id)
        return JobCancelResponse(
            job_id=job_uuid, cancelled=current_app.rest_if.cancel_job(job_uuid)
        )


@api.route("/<string:job_id>/status")
class JobStatusAPI(MethodView):
    """Requests."""

    @api.response(200, JobStatusResponse.Schema())
    def get(self, job_id: str) -> JobStatusResponse | Response:
        """Return job status."""
        job_uuid = uuid.UUID(job_id)
        status = current_app.rest_if.get_job_status(job_uuid)

        result: JobStatusResponse | Response
        if status:
            result = JobStatusResponse(job_id=job_uuid, status=status)
        else:
            result = Response(status=404, response=f"Unknown job {job_id}.")
        return result


@api.route("/<string:job_id>/result")
class JobResultAPI(MethodView):
    """Requests."""

    @api.response(200, JobResultResponse.Schema())
    def get(self, job_id: str) -> JobResultResponse:
        """Return job result with output ESDL (can be None)."""
        job_uuid = uuid.UUID(job_id)
        output_esdl = current_app.rest_if.get_job_output_esdl(job_uuid)
        return JobResultResponse(job_id=job_uuid, output_esdl=output_esdl)


@api.route("/<string:job_id>/logs")
class JobLogsAPI(MethodView):
    """Requests."""

    @api.response(200, JobLogsResponse.Schema())
    def get(self, job_id: str) -> JobLogsResponse:
        """Return job logs."""
        job_uuid = uuid.UUID(job_id)
        logs = current_app.rest_if.get_job_logs(job_uuid)
        if not logs:
            logs = "No logs received for this job."
        return JobLogsResponse(job_id=job_uuid, logs=logs)


@api.route("/user/<string:user_name>")
class JobsByUserAPI(MethodView):
    """Requests."""

    @api.response(200, JobSummary.Schema(many=True))
    def get(self, user_name: str) -> list[JobRest]:
        """Return all jobs from user."""
        return current_app.rest_if.get_jobs_from_user(user_name)


@api.route("/project/<string:project_name>")
class JobByProjectAPI(MethodView):
    """Requests."""

    @api.response(200, JobSummary.Schema(many=True))
    def get(self, project_name: str) -> list[JobRest]:
        """Return all jobs from project."""
        return current_app.rest_if.get_jobs_from_project(project_name)
