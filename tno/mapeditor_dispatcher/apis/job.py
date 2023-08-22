import uuid
from dataclasses import field
from datetime import datetime
from typing import Optional, Dict

from marshmallow_dataclass import dataclass
from flask_smorest import Blueprint

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
class JobStatusResponse:
    job_id: uuid.UUID
    status: JobStatus


@dataclass
class JobResultResponse:
    job_id: uuid.UUID
    output_esdl: Optional[str]


@dataclass
class JobDeleteResponse:
    job_id: uuid.UUID
    deleted: bool


@dataclass
class JobLogsResponse:
    job_id: uuid.UUID
    logs: Optional[str]


@dataclass
class JobDetailsResponse:
    job_id: uuid.UUID
    job_name: str
    work_flow_type: str
    user_name: str
    project_name: str
    status: JobStatus
    input_config: str
    input_esdl: str
    output_esdl: Optional[str]
    added_at: datetime
    running_at: Optional[datetime]
    stopped_at: Optional[datetime]
    logs: Optional[str]


@dataclass
class JobSummary:
    job_id: uuid.UUID
    job_name: str
    user_name: str
    project_name: str
    status: JobStatus
    added_at: datetime
    stopped_at: Optional[datetime]


@api.route("/")
class JobAPI(MethodView):
    @api.arguments(JobInput.Schema())
    @api.response(200, JobStatusResponse.Schema())
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

        return JobStatusResponse(job_id=job_id, status=JobStatus.REGISTERED)

    @api.response(200, JobSummary.Schema(many=True))
    def get(self):
        """
        Return all jobs
        """
        return nwn_client.get_all_jobs()


@api.route("/<string:job_id>")
class JobFromIdAPI(MethodView):
    @api.response(200, JobDetailsResponse.Schema())
    def get(self, job_id: int):
        """
        Return job details
        """
        return nwn_client.get_job_details(job_id)

    @api.response(200, JobDeleteResponse.Schema())
    def delete(self, job_id: int):
        """
        Delete job
        """
        return JobDeleteResponse(job_id=job_id, deleted=nwn_client.delete_job(job_id))


@api.route("/<string:job_id>/status")
class JobStatusAPI(MethodView):
    @api.response(200, JobStatusResponse.Schema())
    def get(self, job_id: int):
        """
        Return job status
        """
        return JobStatusResponse(job_id=job_id, status=nwn_client.get_job_status(job_id))


@api.route("/<string:job_id>/result")
class JobResultAPI(MethodView):
    @api.response(200, JobResultResponse.Schema())
    def get(self, job_id: int):
        """
        Return job result
        """
        return JobResultResponse(job_id=job_id, output_esdl=nwn_client.get_job_output_esdl(job_id))


@api.route("/<string:job_id>/logs")
class JobLogsAPI(MethodView):
    @api.response(200, JobLogsResponse.Schema())
    def get(self, job_id: int):
        """
        Return job logs
        """
        return JobLogsResponse(job_id=job_id, logs=nwn_client.get_job_logs(job_id))


@api.route("/user/<string:user_name>")
class JobsByUserAPI(MethodView):
    @api.response(200, JobSummary.Schema(many=True))
    def get(self, user_name: str):
        """
        Return all jobs from user
        """
        return nwn_client.get_jobs_from_user(user_name)


@api.route("/project/<string:project_name>")
class JobByProjectAPI(MethodView):
    @api.response(200, JobSummary.Schema(many=True))
    def get(self, project_name: str):
        """
        Return all jobs from project
        """
        return nwn_client.get_jobs_from_project(project_name)
