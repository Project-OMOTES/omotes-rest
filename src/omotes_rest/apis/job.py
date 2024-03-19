import base64

from flask_smorest import Blueprint
from flask.views import MethodView

from omotes_rest.apis.api_dataclasses import JobInput, JobCancelInput, JobResponse, \
    JobStatusResponse, JobResultResponse, JobLogsResponse, JobSummary, JobDeleteResponse, \
    JobCancelResponse
from omotes_rest.log import get_logger
from omotes_rest.rest_interface import RestInterface

logger = get_logger("omotes_rest")

api = Blueprint(
    "Job", "Job", url_prefix="/job",
    description="Omotes jobs: start, check status and get overview and results"
)

rest_if = RestInterface()
rest_if.start()


@api.route("/")
class JobAPI(MethodView):
    @api.arguments(JobInput.Schema())
    @api.response(200, JobStatusResponse.Schema())
    def post(self, job_input: JobInput):
        """
        Start new job: 'input_params_dict' can have lists and (nested) dicts as values
        """
        return rest_if.submit_job(job_input)

    @api.response(200, JobSummary.Schema(many=True))
    def get(self):
        """
        Return a summary of all jobs
        """
        return rest_if.get_jobs()


@api.route("/<string:job_id>")
class JobFromIdAPI(MethodView):
    @api.response(200, JobResponse.Schema())
    def get(self, job_id: str):
        """
        Return job details
        """
        return rest_if.get_job(job_id)

    @api.response(200, JobDeleteResponse.Schema())
    def delete(self, job_id: str):
        """
        Delete job, and cancel if queued or running
        """

        return JobDeleteResponse(job_id=job_id,
                                 deleted=rest_if.delete_job(job_id))


@api.route("/cancel")
class JobStatusAPI(MethodView):
    @api.arguments(JobCancelInput.Schema())
    @api.response(200, JobCancelResponse.Schema())
    def put(self, job_cancel_input: JobCancelInput):
        """
        Cancel job if queued or running
        """
        job_id = job_cancel_input.job_id
        return JobCancelResponse(job_id=job_id,
                                 cancelled=rest_if.cancel_job(job_id))


@api.route("/<string:job_id>/status")
class JobStatusAPI(MethodView):
    @api.response(200, JobStatusResponse.Schema())
    def get(self, job_id: str):
        """
        Return job status
        """
        return JobStatusResponse(job_id=job_id,
                                 status=rest_if.get_job_status(job_id))


@api.route("/<string:job_id>/result")
class JobResultAPI(MethodView):
    @api.response(200, JobResultResponse.Schema())
    def get(self, job_id: int):
        """
        Return job result
        """
        output_esdl = rest_if.get_job_output_esdl(job_id)
        b64_esdl = base64.b64encode(bytes(output_esdl, "utf-8")).decode("utf-8")
        return JobResultResponse(job_id=job_id, output_esdl=b64_esdl)


@api.route("/<string:job_id>/logs")
class JobLogsAPI(MethodView):
    @api.response(200, JobLogsResponse.Schema())
    def get(self, job_id: int):
        """
        Return job logs
        """
        return JobLogsResponse(job_id=job_id,
                               logs=rest_if.get_job_logs(job_id))


@api.route("/user/<string:user_name>")
class JobsByUserAPI(MethodView):
    @api.response(200, JobSummary.Schema(many=True))
    def get(self, user_name: str):
        """
        Return all jobs from user
        """
        return rest_if.get_jobs_from_user(user_name)


@api.route("/project/<string:project_name>")
class JobByProjectAPI(MethodView):
    @api.response(200, JobSummary.Schema(many=True))
    def get(self, project_name: str):
        """
        Return all jobs from project
        """
        return rest_if.get_jobs_from_project(project_name)
