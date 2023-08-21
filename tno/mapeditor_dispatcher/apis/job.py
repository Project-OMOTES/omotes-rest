import uuid
from dataclasses import field
from datetime import datetime
from typing import Optional, Dict

from marshmallow_dataclass import dataclass
from flask_smorest import Blueprint, abort

from flask.views import MethodView

from tno.mapeditor_dispatcher.database import session_scope
from tno.mapeditor_dispatcher.dbmodels import NwnJob
from tno.mapeditor_dispatcher.settings import EnvSettings
from tno.shared.log import get_logger
from nwnsdk import NwnClient, PostgresConfig, RabbitmqConfig, WorkFlowType, JobStatus

logger = get_logger(__name__)

postgres_config = PostgresConfig(
    EnvSettings.nwn_postgres_host(),
    EnvSettings.nwn_postgres_port(),
    EnvSettings.nwn_postgres_database_name(),
    EnvSettings.nwn_postgres_user(),
    EnvSettings.nwn_postgres_password(),
)
rabbitmq_config = RabbitmqConfig(
    EnvSettings.nwn_rabbitmq_host(),
    EnvSettings.nwn_rabbitmq_port(),
    EnvSettings.nwn_rabbitmq_exchange(),
    EnvSettings.nwn_rabbitmq_user(),
    EnvSettings.nwn_rabbitmq_password(),
    EnvSettings.nwn_rabbitmq_hipe_compile(),
)
nwn_client = NwnClient(postgres_config, rabbitmq_config)
api = Blueprint(
    "Job", "Job", url_prefix="/job", description="NWN jobs: start, check status and get overview and results"
)


@dataclass
class JobInput:
    job_name: str
    work_flow_type: WorkFlowType
    user_name: str
    project_name: str
    input_esdl: str
    input_config: Optional[Dict] = field(metadata=dict(required=False))


@dataclass
class JobPostResponse:
    job_id: uuid.UUID
    status: str


@dataclass
class JobDetails:
    job_id: uuid.UUID
    job_name: str
    work_flow_type: str
    user_name: str
    project_name: str
    status: str
    input_config: str
    input_esdl: str
    output_esdl: Optional[str]
    added_at: datetime
    running_at: Optional[datetime]
    stopped_at: Optional[datetime]
    log: Optional[str]


@dataclass
class JobSummary:
    job_id: uuid.UUID
    job_name: str
    user_name: str
    project_name: str
    status: str
    added_at: datetime


#
# @dataclass
# class LogResponse:
#     job_id: int
#     log: str
#
#
# @dataclass
# class ESDLResultResponse:
#     job_id: int
#     esdl: str


@api.route("/")
class JobAPI(MethodView):
    @api.arguments(JobInput.Schema())
    @api.response(200, JobPostResponse.Schema())
    def post(self, request: JobInput):
        """
        Start new job
        """
        job_id = nwn_client.start_work_flow(
            request.work_flow_type, request.job_name, request.input_esdl, request.user_name, request.project_name
        )
        with session_scope() as session:
            new_job = NwnJob(job_id=job_id, user_name=request.user_name, project_name=request.project_name)
            session.add(new_job)

        return JobPostResponse(job_id=job_id, status=JobStatus.REGISTERED)

    @api.response(200, JobSummary.Schema(many=True))
    def get(self):
        """
        Return all jobs
        """
        return nwn_client.get_all_jobs()


@api.route("/<string:job_id>")
class JobDetails(MethodView):
    @api.response(200, JobDetails.Schema())
    def get(self, job_id: int):
        """
        Return job details
        """
        return nwn_client.get_job_details(job_id)


@api.route("/user/<string:user_name>")
class JobByUser(MethodView):
    @api.response(200, JobSummary.Schema(many=True))
    def get(self, user_name: str):
        """
        Return all jobs from user
        """
        return nwn_client.get_jobs_from_user(user_name)


@api.route("/project/<string:project_name>")
class JobByProject(MethodView):
    @api.response(200, JobSummary.Schema(many=True))
    def get(self, project_name: str):
        """
        Return all jobs from project
        """
        return nwn_client.get_jobs_from_project(project_name)


# @api.route("/job/<int:id>")
# class GetJob(MethodView):
#     """
#     Returns a specific job
#     """
#
#     @api.response(200, JobDetails.Schema(many=False))
#     def get(self, job_id: int):
#         print(job_id)
#         return JobDetails(username="Ewoud", id=job_id, name="First run", status="FINISHED", timestamp=datetime.now())
#
#
# @api.route("/job/log/<int:id>")
# class GetLog(MethodView):
#     """
#     Returns the logging of the workflow for a specific Job
#     """
#
#     @api.response(200, LogResponse.Schema())
#     def get(self, job_id: int):
#         print(job_id)
#         return LogResponse(job_id=job_id, log="This is a log with no errors")
#
#
# @api.route("/job/result/<int:id>")
# class GetESDLResult(MethodView):
#     """
#     Returns the ESDL result of a specific job, if available
#     """
#
#     @api.response(200, ESDLResultResponse.Schema())
#     def get(self, job_id: int):
#         print(job_id)
#         if None:  # check if result is available first
#             abort(404, message="Job is not finished. Current state is: Running")
#         # b64 encode esdl string
#         return ESDLResultResponse(job_id=job_id, esdl="<EnergySystem/>")
