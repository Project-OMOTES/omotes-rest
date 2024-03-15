from flask_smorest import Blueprint
from flask.views import MethodView

from omotes_rest import omotes_actions
from omotes_rest.apis.api_dataclasses import JobInput, JobStatusResponse
from omotes_rest.log import get_logger


logger = get_logger("omotes_rest")

api = Blueprint(
    "Job", "Job", url_prefix="/job",
    description="Omotes jobs: start, check status and get overview and results"
)


@api.route("/")
class JobAPI(MethodView):
    @api.arguments(JobInput.Schema())
    @api.response(200, JobStatusResponse.Schema())
    def post(self, job_input: JobInput):
        """
        Start new job
        """
        return omotes_actions.submit_job(job_input)

    # @api.response(200, JobSummary.Schema(many=True))
    # def get(self):
    #     """
    #     Return all jobs
    #     """
    #     return nwn_client.get_all_jobs()

# @api.route("/<string:job_id>")
# class JobFromIdAPI(MethodView):
#     @api.response(200, JobDetailsResponse.Schema())
#     def get(self, job_id: int):
#         """
#         Return job details
#         """
#         return nwn_client.get_job_details(job_id)
#
#     @api.response(200, JobDeleteResponse.Schema())
#     def delete(self, job_id: int):
#         """
#         Delete job
#         """
#         return JobDeleteResponse(job_id=job_id, deleted=nwn_client.delete_job(job_id))
#
#
# @api.route("/<string:job_id>/status")
# class JobStatusAPI(MethodView):
#     @api.response(200, JobStatusResponse.Schema())
#     def get(self, job_id: int):
#         """
#         Return job status
#         """
#         return JobStatusResponse(job_id=job_id, status=nwn_client.get_job_status(job_id))
#
#
# @api.route("/<string:job_id>/result")
# class JobResultAPI(MethodView):
#     @api.response(200, JobResultResponse.Schema())
#     def get(self, job_id: int):
#         """
#         Return job result
#         """
#         output_esdl = nwn_client.get_job_output_esdl(job_id)
#         b64_esdl = base64.b64encode(bytes(output_esdl, "utf-8")).decode("utf-8")
#         return JobResultResponse(job_id=job_id, output_esdl=b64_esdl)
#
#
# @api.route("/<string:job_id>/logs")
# class JobLogsAPI(MethodView):
#     @api.response(200, JobLogsResponse.Schema())
#     def get(self, job_id: int):
#         """
#         Return job logs
#         """
#         return JobLogsResponse(job_id=job_id, logs=nwn_client.get_job_logs(job_id))
#
#
# @api.route("/user/<string:user_name>")
# class JobsByUserAPI(MethodView):
#     @api.response(200, JobSummary.Schema(many=True))
#     def get(self, user_name: str):
#         """
#         Return all jobs from user
#         """
#         return nwn_client.get_jobs_from_user(user_name)
#
#
# @api.route("/project/<string:project_name>")
# class JobByProjectAPI(MethodView):
#     @api.response(200, JobSummary.Schema(many=True))
#     def get(self, project_name: str):
#         """
#         Return all jobs from project
#         """
#         return nwn_client.get_jobs_from_project(project_name)
