import base64
from datetime import timedelta
from uuid import uuid4

from omotes_sdk.omotes_interface import OmotesInterface
from omotes_sdk.internal.common.config import EnvRabbitMQConfig
from omotes_sdk.omotes_interface import (
    Job,
    JobResult,
    JobProgressUpdate,
    JobStatusUpdate,
)
from omotes_sdk.workflow_type import WorkflowType

from omotes_rest.log import get_logger
from omotes_rest.postgres_interface import PostgresInterface
from omotes_rest.config import PostgreSQLConfig
from omotes_rest.apis.api_dataclasses import JobInput, JobStatusResponse
from omotes_rest.db_models.job_rest import JobRestStatus, JobRest

logger = get_logger("omotes_rest")


class RestInterface:
    def __init__(self):
        self.omotes_if = OmotesInterface(EnvRabbitMQConfig())
        self.postgres_if = PostgresInterface(PostgreSQLConfig())

    def start(self) -> None:
        self.omotes_if.start()
        self.postgres_if.start()

    def handle_on_job_finished(self, job: Job, result: JobResult) -> None:
        self.postgres_if.set_job_status(
            job_id=job.id,
            new_status=3,  # FINISHED
            result=result,
        )

    def handle_on_job_status_update(self, job: Job, status_update: JobStatusUpdate) -> None:
        self.postgres_if.set_job_status(
            job_id=job.id,
            new_status=status_update.status,
        )

    def handle_on_job_progress_update(self, job: Job, progress_update: JobProgressUpdate) -> None:
        self.postgres_if.set_job_progress(
            job_id=job.id,
            progress_fraction=progress_update.progress,
            progress_message=progress_update.message,
        )

    def submit_job(self, job_input: JobInput) -> JobStatusResponse:
        job = self.omotes_if.submit_job(
            esdl=base64.b64decode(job_input.input_esdl).decode(),
            params_dict=job_input.input_params_dict,
            workflow_type=WorkflowType(workflow_type_name=job_input.workflow_type,
                                       workflow_type_description_name="some descr"),
            job_timeout=timedelta(seconds=job_input.timeout_after_s),
            callback_on_finished=self.handle_on_job_finished,
            callback_on_progress_update=self.handle_on_job_progress_update,
            callback_on_status_update=self.handle_on_job_status_update,
            auto_disconnect_on_result=True
        )
        self.postgres_if.put_new_job(
            job_id=job.id,
            job_input=job_input,
        )
        return JobStatusResponse(job_id=job.id, status=JobRestStatus.REGISTERED)

    def get_job(self, job_id: uuid4):
        return self.postgres_if.get_job(job_id)

    def get_jobs(self) -> list[JobRest]:
        return self.postgres_if.get_jobs()

    def cancel_job(self, job_id: uuid4) -> bool:
        job = Job(
            id=job_id,
            workflow_type=WorkflowType(
                workflow_type_name=self.get_job(job_id).workflow_type,
                workflow_type_description_name="some descr"
            )
        )
        self.omotes_if.cancel_job(job)
        return True

    def delete_job(self, job_id: uuid4) -> bool:
        self.cancel_job(job_id)
        return self.postgres_if.delete_job(job_id)

    def get_job_status(self, job_id: uuid4) -> JobRestStatus:
        return self.postgres_if.get_job_status(job_id)

    def get_job_output_esdl(self, job_id: uuid4) -> str:
        return self.postgres_if.get_job_output_esdl(job_id)

    def get_job_logs(self, job_id: uuid4) -> str:
        return self.postgres_if.get_job_logs(job_id)

    def get_jobs_from_user(self, user_name: str) -> list[JobRest]:
        return self.postgres_if.get_jobs_from_user(user_name)

    def get_jobs_from_project(self, user_name: str) -> list[JobRest]:
        return self.postgres_if.get_jobs_from_project(user_name)
