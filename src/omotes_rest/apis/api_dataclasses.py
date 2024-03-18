import json
import uuid
from enum import Enum
from marshmallow_dataclass import dataclass


class WorkFlowName(Enum):
    GROW_OPTIMIZER = "grow_optimizer"
    GROW_SIMULATOR = "grow_simulator"
    GROW_OPTIMIZER_NO_HEAT_LOSSES = "grow_optimizer_no_heat_losses"
    GROW_OPTIMIZER_NO_HEAT_LOSSES_DISCOUNTED_CAPEX = "grow_optimizer_no_heat_losses" \
                                                     "_discounted_capex"
    SIMULATOR = "simulator"


class JobRestStatus(Enum):
    """Phases a job progresses through.

    Note: The job is removed when it is finished (regardless of the result type). Therefor
    this state is not defined in this `Enum`.
    """
    REGISTERED = "registered"
    """Job is registered but not yet running."""
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


@dataclass
class JobInput:
    job_name: str = "job name"
    work_flow_name: WorkFlowName = WorkFlowName.GROW_OPTIMIZER
    user_name: str = "user name"
    input_esdl: str = "input ESDL string"
    project_name: str = "project name"
    input_params_dict_str: str = json.dumps(
        {'key1': "value1", "key2": ["just", "a", "list", "with", "an", "integer", 3]})
    timeout_after_s: int = 3600


@dataclass
class JobStatusResponse:
    job_id: uuid.UUID
    status: JobRestStatus

# @dataclass
# class JobResultResponse:
#     job_id: uuid.UUID
#     output_esdl: Optional[str]
#
#
# @dataclass
# class JobDeleteResponse:
#     job_id: uuid.UUID
#     deleted: bool
#
#
# @dataclass
# class JobLogsResponse:
#     job_id: uuid.UUID
#     logs: Optional[str]
#
#
# @dataclass
# class JobDetailsResponse:
#     job_id: uuid.UUID
#     job_name: str
#     work_flow_type: str
#     user_name: str
#     project_name: str
#     status: JobStatus
#     input_config: str
#     input_esdl: str
#     output_esdl: Optional[str]
#     added_at: datetime
#     running_at: Optional[datetime]
#     stopped_at: Optional[datetime]
#     logs: Optional[str]
#
#
# @dataclass
# class JobSummary:
#     job_id: uuid.UUID
#     job_name: str
#     user_name: str
#     project_name: str
#     status: JobStatus
#     added_at: datetime
#     stopped_at: Optional[datetime]
