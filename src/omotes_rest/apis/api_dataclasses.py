import uuid
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

from marshmallow_dataclass import dataclass
from marshmallow_dataclass import add_schema


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

    job_name: str = "job name"
    workflow_type: str = "grow_optimizer"
    user_name: str = "user name"
    input_esdl: str = "input ESDL base64string"
    project_name: str = "project name"
    input_params_dict: dict[str, Any] = field(default_factory=dict)
    timeout_after_s: int = 3600


@add_schema
@dataclass
class JobStatusResponse:
    """Response with job status."""

    job_id: uuid.UUID
    status: JobRestStatus


@add_schema
@dataclass
class JobResultResponse:
    """Response with job result."""

    job_id: uuid.UUID
    output_esdl: str | None


@add_schema
@dataclass
class JobDeleteResponse:
    """Response for job deletion."""

    job_id: uuid.UUID
    deleted: bool


@add_schema
@dataclass
class JobCancelResponse:
    """Response for job cancellation."""

    job_id: uuid.UUID
    cancelled: bool


@add_schema
@dataclass
class JobLogsResponse:
    """Response with job logs."""

    job_id: uuid.UUID
    logs: str | None


@add_schema
@dataclass
class JobResponse:
    """Response with all job data."""

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


@add_schema
@dataclass
class JobSummary:
    """Response with job summary used in job lists."""

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
