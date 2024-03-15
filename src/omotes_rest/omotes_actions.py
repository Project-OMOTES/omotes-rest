import base64
import json
from datetime import timedelta

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
from omotes_rest.db_models.job_rest import JobRestStatus

logger = get_logger("omotes_rest")

omotes_if = OmotesInterface(EnvRabbitMQConfig())
omotes_if.start()

postgres_if = PostgresInterface(PostgreSQLConfig())
postgres_if.start()


def handle_on_job_finished(job: Job, result: JobResult) -> None:
    postgres_if.set_job_status(
        job_id=job.id,
        new_status=3,  # FINISHED
        result_type=result.result_type,
    )


def handle_on_job_status_update(job: Job, status_update: JobStatusUpdate) -> None:
    postgres_if.set_job_status(
        job_id=job.id,
        new_status=status_update.status,
    )


def handle_on_job_progress_update(job: Job, progress_update: JobProgressUpdate) -> None:
    postgres_if.set_job_progress(
        job_id=job.id,
        progress_fraction=progress_update.progress,
        progress_message=progress_update.message,
    )


def submit_job(job_input: JobInput) -> JobStatusResponse:
    job = omotes_if.submit_job(
        esdl=base64.b64decode(job_input.input_esdl).decode(),
        params_dict=json.loads(job_input.input_params_dict_str),
        workflow_type=WorkflowType(workflow_type_name=job_input.work_flow_name.value,
                                   workflow_type_description_name="some descr"),
        job_timeout=timedelta(seconds=job_input.timeout_after_s),
        callback_on_finished=handle_on_job_finished,
        callback_on_progress_update=handle_on_job_progress_update,
        callback_on_status_update=handle_on_job_status_update,
        auto_disconnect_on_result=True
    )
    postgres_if.put_new_job(
        job_id=job.id,
        job_input=job_input,
    )
    return JobStatusResponse(job_id=job.id, status=JobRestStatus.REGISTERED)
