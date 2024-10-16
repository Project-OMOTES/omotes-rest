import uuid
from datetime import timedelta, datetime
from typing import Union, Any

from omotes_sdk.types import ParamsDict
from omotes_sdk.omotes_interface import OmotesInterface
from omotes_sdk.internal.common.config import EnvRabbitMQConfig
from omotes_sdk.omotes_interface import (
    Job,
    JobResult,
    JobProgressUpdate,
    JobStatusUpdate,
)
import omotes_sdk.workflow_type
from omotes_sdk.workflow_type import (
    StringParameter,
    BooleanParameter,
    IntegerParameter,
    FloatParameter,
    DateTimeParameter,
    DurationParameter,
    WorkflowType,
)

import logging
from omotes_rest.postgres_interface import PostgresInterface
from omotes_rest.config import PostgresConfig
from omotes_rest.apis.api_dataclasses import JobInput, JobStatusResponse
from omotes_rest.db_models.job_rest import JobRestStatus, JobRest
from omotes_rest.settings import EnvSettings

logger = logging.getLogger("omotes_rest")


def convert_json_forms_values_to_params_dict(
    workflow_type: WorkflowType, input_params_dict: dict[str, Any]
) -> ParamsDict:
    """Convert values received from the JSON forms format to the omotes params_dict format.

    :param workflow_type: The workflow type for which these JSON format values were received.
    :param input_params_dict: Dictionary of values in JSON forms format.
    :return: The omotes params_dict.
    """
    params_dict: ParamsDict = {}
    if workflow_type.workflow_parameters:
        for parameter in workflow_type.workflow_parameters:
            json_forms_value = input_params_dict.get(parameter.key_name)

            if json_forms_value is None:
                raise RuntimeError(f"Missing parameter {parameter.key_name} in job submission.")

            match type(parameter):
                case omotes_sdk.workflow_type.DurationParameter:
                    params_dict[parameter.key_name] = timedelta(seconds=json_forms_value)
                case omotes_sdk.workflow_type.DateTimeParameter:
                    params_dict[parameter.key_name] = datetime.fromisoformat(json_forms_value)
                case _:
                    params_dict[parameter.key_name] = json_forms_value

    return params_dict


class RestInterface:
    """Interface specifically for the Omotes Rest service."""

    omotes_if: OmotesInterface
    """Interface to Omotes."""
    postgres_if: PostgresInterface
    """Interface to Omotes rest postgres."""

    def __init__(
        self,
    ) -> None:
        """Create the omotes rest interface."""
        self.omotes_if = OmotesInterface(EnvRabbitMQConfig(), EnvSettings.omotes_id())
        self.postgres_if = PostgresInterface(PostgresConfig())

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
            job_id=job.id, new_status=final_status, logs=result.logs, output_esdl=result.output_esdl
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

    def get_workflows_jsonforms_format(self) -> list:
        """Get the available workflows with jsonforms schema for the non-ESDL parameters.

        :return: dictionary response.
        """
        workflows = []
        for _workflow in self.omotes_if.get_workflow_type_manager().get_all_workflows():
            properties = dict()
            required_props = []
            uischema = dict(type="VerticalLayout", elements=[])
            if _workflow.workflow_parameters:
                for _parameter in _workflow.workflow_parameters:
                    jsonforms_schema: dict[
                        str, Union[str, float, datetime, list[dict[str, str]]]
                    ] = dict()
                    if _parameter.title:
                        jsonforms_schema["title"] = _parameter.title
                    if _parameter.description:
                        jsonforms_schema["description"] = _parameter.description

                    if isinstance(_parameter, StringParameter):
                        jsonforms_schema["type"] = "string"
                        if _parameter.default:
                            jsonforms_schema["default"] = _parameter.default
                        if _parameter.enum_options:
                            one_of_list = []
                            for enum_option in _parameter.enum_options:
                                one_of_list.append(
                                    dict(const=enum_option.key_name, title=enum_option.display_name)
                                )
                            jsonforms_schema["oneOf"] = one_of_list
                    elif isinstance(_parameter, BooleanParameter):
                        jsonforms_schema["type"] = "boolean"
                        if _parameter.default:
                            jsonforms_schema["default"] = _parameter.default
                    elif isinstance(_parameter, IntegerParameter):
                        jsonforms_schema["type"] = "integer"
                        if _parameter.default:
                            jsonforms_schema["default"] = _parameter.default
                        if _parameter.minimum:
                            jsonforms_schema["minimum"] = _parameter.minimum
                        if _parameter.maximum:
                            jsonforms_schema["maximum"] = _parameter.maximum
                    elif isinstance(_parameter, FloatParameter):
                        jsonforms_schema["type"] = "number"
                        if _parameter.default:
                            jsonforms_schema["default"] = _parameter.default
                        if _parameter.minimum:
                            jsonforms_schema["minimum"] = _parameter.minimum
                        if _parameter.maximum:
                            jsonforms_schema["maximum"] = _parameter.maximum
                    elif isinstance(_parameter, DateTimeParameter):
                        jsonforms_schema["type"] = "string"
                        jsonforms_schema["format"] = "date-time"
                        if _parameter.default:
                            jsonforms_schema["default"] = _parameter.default.isoformat()
                    elif isinstance(_parameter, DurationParameter):
                        jsonforms_schema["type"] = "number"
                        if _parameter.default:
                            jsonforms_schema["default"] = _parameter.default.total_seconds()
                        if _parameter.minimum:
                            jsonforms_schema["minimum"] = _parameter.minimum.total_seconds()
                        if _parameter.maximum:
                            jsonforms_schema["maximum"] = _parameter.maximum.total_seconds()
                    else:
                        raise NotImplementedError(
                            f"Parameter type {type(_parameter)} not supported"
                        )
                    properties[_parameter.key_name] = jsonforms_schema
                    required_props.append(_parameter.key_name)
                    if isinstance(uischema["elements"], list):
                        uischema["elements"].append(
                            {
                                "type": "Control",
                                "scope": f"#/properties/{_parameter.key_name}",
                            }
                        )

            if properties:
                workflows.append(
                    dict(
                        id=_workflow.workflow_type_name,
                        description=_workflow.workflow_type_description_name,
                        schema=dict(type="object", properties=properties, required=required_props),
                        uischema=uischema,
                    )
                )
            else:
                workflows.append(
                    dict(
                        id=_workflow.workflow_type_name,
                        description=_workflow.workflow_type_description_name,
                    )
                )
        return workflows

    def submit_job(self, job_input: JobInput) -> JobStatusResponse:
        """When a job has a progress update.

        :param job_input: JobInput dataclass with job input.
        :return: JobStatusResponse.
        """
        workflow_type = self.omotes_if.get_workflow_type_manager().get_workflow_by_name(
            job_input.workflow_type
        )
        if not workflow_type:
            raise RuntimeError(f"Unknown workflow type {job_input.workflow_type}")

        params_dict = convert_json_forms_values_to_params_dict(
            workflow_type, job_input.input_params_dict
        )

        job = self.omotes_if.submit_job(
            esdl=job_input.input_esdl,
            job_reference=job_input.job_name,
            params_dict=params_dict,
            workflow_type=workflow_type,
            job_timeout=timedelta(seconds=job_input.timeout_after_s),
            callback_on_finished=self.handle_on_job_finished,
            callback_on_progress_update=self.handle_on_job_progress_update,
            callback_on_status_update=self.handle_on_job_status_update,
            auto_disconnect_on_result=True,
        )
        self.postgres_if.put_new_job(
            job_id=job.id,
            job_input=job_input,
            esdl_input=job_input.input_esdl,
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
            workflow_type = self.omotes_if.get_workflow_type_manager().get_workflow_by_name(
                job_in_db.workflow_type
            )
            if not workflow_type:
                raise RuntimeError(f"Unknown workflow type {job_in_db.workflow_type}")

            job = Job(id=job_id, workflow_type=workflow_type)
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
