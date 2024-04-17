import base64
import uuid
from datetime import timedelta

from omotes_sdk.omotes_interface import OmotesInterface
from omotes_sdk.internal.common.config import EnvRabbitMQConfig
from omotes_sdk.omotes_interface import (
    Job,
    JobResult,
    JobProgressUpdate,
    JobStatusUpdate,
)
from omotes_sdk.workflow_type import WorkflowTypeManager

import logging
from omotes_rest.postgres_interface import PostgresInterface
from omotes_rest.config import POSTGRESConfig
from omotes_rest.apis.api_dataclasses import JobInput, JobStatusResponse
from omotes_rest.db_models.job_rest import JobRestStatus, JobRest
from omotes_rest.workflows import FRONTEND_NAME_TO_OMOTES_WORKFLOW_NAME

logger = logging.getLogger("omotes_rest")


class RestInterface:
    """Interface specifically for the Omotes Rest service."""

    omotes_if: OmotesInterface
    """Interface to Omotes."""
    postgres_if: PostgresInterface
    """Interface to Omotes rest postgres."""
    workflow_type_manager: WorkflowTypeManager
    """Interface to Omotes."""

    def __init__(self, workflow_type_manager: WorkflowTypeManager):
        """Create the omotes rest interface.

        :param workflow_type_manager: All available OMOTES workflow types.
        """
        self.omotes_if = OmotesInterface(EnvRabbitMQConfig(), workflow_type_manager)
        self.postgres_if = PostgresInterface(POSTGRESConfig())
        self.workflow_type_manager = workflow_type_manager

    def start(self) -> None:
        """Start the omotes rest interface."""
        self.omotes_if.start()
        self.postgres_if.start()

    def stop(self) -> None:
        """Stop the omotes rest interface."""
        self.omotes_if.stop()

    def handle_on_job_finished(self, job: Job, result: JobResult) -> None:
        """When a job is finished.

        :param job: Omotes job.
        :param result: JobResult protobuf message.
        """
        if result.result_type == JobResult.ResultType.SUCCEEDED:
            final_status = JobRestStatus.SUCCEEDED
        elif result.result_type == JobResult.ResultType.TIMEOUT:
            final_status = JobRestStatus.TIMEOUT
        elif result.result_type == JobResult.ResultType.ERROR:
            final_status = JobRestStatus.ERROR
        elif result.result_type == JobResult.ResultType.CANCELLED:
            final_status = JobRestStatus.CANCELLED
        else:
            raise NotImplementedError(f"Unknown result type '{result.result_type}'")

        self.postgres_if.set_job_stopped(
            job_id=job.id,
            new_status=final_status,
            logs=result.logs,
            output_esdl=result.output_esdl
        )

    def handle_on_job_status_update(self, job: Job, status_update: JobStatusUpdate) -> None:
        """When a job has a status update.

        :param job: Omotes job.
        :param status_update: JobStatusUpdate protobuf message.
        """
        if status_update.status == JobStatusUpdate.JobStatus.REGISTERED:
            self.postgres_if.set_job_registered(job.id)
        elif status_update.status == JobStatusUpdate.JobStatus.ENQUEUED:
            self.postgres_if.set_job_enqueued(job.id)
        elif status_update.status == JobStatusUpdate.JobStatus.RUNNING:
            self.postgres_if.set_job_running(job.id)
        elif status_update.status == JobStatusUpdate.JobStatus.FINISHED:
            self.postgres_if.set_job_stopped(
                job_id=job.id,
                new_status=JobRestStatus.SUCCEEDED,
            )
        elif status_update.status == JobStatusUpdate.JobStatus.CANCELLED:
            self.postgres_if.set_job_stopped(
                job_id=job.id,
                new_status=JobRestStatus.CANCELLED,
            )
        else:
            raise NotImplementedError(f"Unknown update status '{status_update.status}'")

    def handle_on_job_progress_update(self, job: Job, progress_update: JobProgressUpdate) -> None:
        """When a job has a progress update.

        :param job: Omotes job.
        :param progress_update: JobProgressUpdate protobuf message.
        """
        self.postgres_if.set_job_progress(
            job_id=job.id,
            progress_fraction=progress_update.progress,
            progress_message=progress_update.message,
        )

    def submit_job(self, job_input: JobInput) -> JobStatusResponse:
        """When a job has a progress update.

        :param job_input: JobInput dataclass with job input.
        :return: JobStatusResponse.
        """
        esdlstr_bytes = job_input.input_esdl.encode('utf-8')
        esdlstr_base64_bytes = base64.b64decode(esdlstr_bytes)
        esdl_str = esdlstr_base64_bytes.decode('utf-8')
        job = self.omotes_if.submit_job(
            esdl=esdl_str,
            params_dict=job_input.input_params_dict,
            workflow_type=self.workflow_type_manager.get_workflow_by_name(FRONTEND_NAME_TO_OMOTES_WORKFLOW_NAME[job_input.workflow_type]),
            job_timeout=timedelta(seconds=job_input.timeout_after_s),
            callback_on_finished=self.handle_on_job_finished,
            callback_on_progress_update=self.handle_on_job_progress_update,
            callback_on_status_update=self.handle_on_job_status_update,
            auto_disconnect_on_result=True
        )
        self.postgres_if.put_new_job(
            job_id=job.id,
            job_input=job_input,
            esdl_input=esdl_str,
        )
        return JobStatusResponse(job_id=job.id, status=JobRestStatus.REGISTERED)

    def get_job(self, job_id: uuid.UUID) -> JobRest | None:
        """Get job by id.

        :param job_id: Job id.
        :return: JobRest if found, else None.
        """
        return self.postgres_if.get_job(job_id)

    def get_jobs(self) -> list[JobRest]:
        """Get list of all jobs.

        :return: List of jobs.
        """
        return self.postgres_if.get_jobs()

    def cancel_job(self, job_id: uuid.UUID) -> bool:
        """Cancel job by id.

        :param job_id: Job id.
        :return: True if job found and cancelled.
        """
        job_in_db = self.get_job(job_id)

        if job_in_db:
            job = Job(
                id=job_id,
                workflow_type=self.workflow_type_manager.get_workflow_by_name(FRONTEND_NAME_TO_OMOTES_WORKFLOW_NAME[job_in_db.workflow_type])
            )
            self.omotes_if.cancel_job(job)
            result = True
        else:
            result = False
        return result

    def delete_job(self, job_id: uuid.UUID) -> bool:
        """Delete job by id.

        :param job_id: Job id.
        :return: True if job found and deleted.
        """
        self.cancel_job(job_id)
        return self.postgres_if.delete_job(job_id)

    def get_job_status(self, job_id: uuid.UUID) -> JobRestStatus | None:
        """Get job status by id.

        :param job_id: Job id.
        :return: JobRestStatus if found, else None.
        """
        return self.postgres_if.get_job_status(job_id)

    def get_job_output_esdl(self, job_id: uuid.UUID) -> str | None:
        """Get job output ESDL by id.

        :param job_id: Job id.
        :return: Output ESDL base64 string if found, else None.
        """
        return self.postgres_if.get_job_output_esdl(job_id)

    def get_job_logs(self, job_id: uuid.UUID) -> str | None:
        """Get job logs by id.

        :param job_id: Job id.
        :return: logs as string if found, else None.
        """
        return self.postgres_if.get_job_logs(job_id)

    def get_jobs_from_user(self, user_name: str) -> list[JobRest]:
        """Get list of all jobs from a specific user.

        :param user_name: Name of the user.
        :return: List of jobs.
        """
        return self.postgres_if.get_jobs_from_user(user_name)

    def get_jobs_from_project(self, user_name: str) -> list[JobRest]:
        """Get list of all jobs from a specific project.

        :param user_name: Name of the project.
        :return: List of jobs.
        """
        return self.postgres_if.get_jobs_from_project(user_name)
