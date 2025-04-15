import uuid
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Type, Optional

from marshmallow import Schema, validate
from marshmallow.fields import String
from marshmallow_dataclass import add_schema, dataclass


@add_schema
@dataclass
class WorkflowResponse:
    """Response with available workflows."""

    Schema: ClassVar[Type[Schema]] = Schema

    workflow_type_name: str
    workflow_type_description_name: str
    workflow_parameters: dict[str, Any] | None


class JobRestStatus(Enum):
    """Possible job status."""

    REGISTERED = "registered"
    """Job is registered but not yet submitted to Celery."""
    ENQUEUED = "enqueued"
    """Job is submitted to Celery but not yet started."""
    RUNNING = "running"
    """Job is started and waiting to complete."""
    SUCCEEDED = "succeeded"
    """Job is finished successfully."""
    CANCELLED = "cancelled"
    """Job was cancelled."""
    TIMEOUT = "timeout"
    """Job ended due to a timeout."""
    ERROR = "error"
    """Job ended due to an error."""


@add_schema
@dataclass
class JobInput:
    """Input needed to start a new job."""

    Schema: ClassVar[Type[Schema]] = Schema

    job_name: str = "job name"
    workflow_type: str = "grow_optimizer_no_heat_losses"
    user_name: str = "user name"
    input_esdl: str = "input ESDL base64string"
    project_name: str = "project name"
    input_params_dict: dict[str, Any] = field(default_factory=dict)
    timeout_after_s: int = 3600
    job_priority: Optional[str] = field(
        default=None,
        metadata={
            "marshmallow_field": String(
                allow_none=True,
                validate=validate.OneOf(["medium", "low", "high"])
            )
        }
    )


@add_schema
@dataclass
class JobStatusResponse:
    """Response with job status."""

    Schema: ClassVar[Type[Schema]] = Schema

    job_id: uuid.UUID
    status: JobRestStatus


@add_schema
@dataclass
class JobResultResponse:
    """Response with job result."""

    Schema: ClassVar[Type[Schema]] = Schema

    job_id: uuid.UUID
    output_esdl: str | None


@add_schema
@dataclass
class JobDeleteResponse:
    """Response for job deletion."""

    Schema: ClassVar[Type[Schema]] = Schema

    job_id: uuid.UUID
    deleted: bool


@add_schema
@dataclass
class JobLogsResponse:
    """Response with job logs."""

    Schema: ClassVar[Type[Schema]] = Schema

    job_id: uuid.UUID
    logs: str | None


@add_schema
@dataclass
class JobResponse:
    """Response with all job data."""

    Schema: ClassVar[Type[Schema]] = Schema

    job_id: uuid.UUID
    job_name: str
    workflow_type: str
    status: JobRestStatus
    progress_fraction: float
    progress_message: str
    registered_at: datetime
    submitted_at: datetime | datetime
    running_at: datetime | datetime
    stopped_at: datetime | datetime
    timeout_after_s: int
    user_name: str
    project_name: str
    input_params_dict: dict
    input_esdl: str
    output_esdl: str
    logs: str
    esdl_feedback: dict[str, list]
    job_priority: str


@add_schema
@dataclass
class JobSummary:
    """Response with job summary used in job lists."""

    Schema: ClassVar[Type[Schema]] = Schema

    job_id: uuid.UUID
    job_name: str
    workflow_type: str
    status: JobRestStatus
    progress_fraction: float
    registered_at: datetime
    running_at: datetime | datetime
    stopped_at: datetime | datetime
    user_name: str
    project_name: str
