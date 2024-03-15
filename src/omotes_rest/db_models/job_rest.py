import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

from omotes_rest.apis.api_dataclasses import WorkFlowName, JobRestStatus

Base = declarative_base()


@dataclass
class JobRest(Base):
    """SQL table definition for an Omotes job.
    """

    __tablename__ = "job_rest"

    job_id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True)  # type: ignore [misc]
    """OMOTES identifier for the job."""
    job_name: str = db.Column(db.String, nullable=False)
    """Job name/description."""
    work_flow_name: WorkFlowName = db.Column(db.Enum(WorkFlowName), nullable=False)
    """Name of the workflow this job runs."""
    status: JobRestStatus = db.Column(db.Enum(JobRestStatus), nullable=False)
    """Last received status of the job."""
    progress_fraction: float = db.Column(db.Float, nullable=False)
    """Last received progress (fraction) of the job."""
    progress_message: str = db.Column(db.String, nullable=False)
    """Last received progress (fraction) of the job."""
    registered_at: datetime = db.Column(db.DateTime(timezone=True), nullable=False)
    """Time at which the job is registered."""
    submitted_at: Optional[datetime] = db.Column(db.DateTime(timezone=True))
    """Time at which the job is submitted to Celery."""
    running_at: Optional[datetime] = db.Column(db.DateTime(timezone=True))
    """Time at which a Celery worker has started the task for this job."""
    stopped_at: Optional[datetime] = db.Column(db.DateTime(timezone=True))
    """Time at which the job stopped: due to finish, error or cancel."""
    timeout_after_s: int = db.Column(db.Integer)
    """Duration the job may run for before being cancelled due to timing out."""
    user_name: str = db.Column(db.String, nullable=False)
    """User name of job submitter."""
    project_name: str = db.Column(db.String, nullable=False)
    """Project name that the job belongs to."""
    input_params_dict_str: str = db.Column(db.String)
    """Dictionary of 'non-ESDL' input parameters as string."""
    input_esdl: str = db.Column(db.String, nullable=False)
    """Input ESDL as string."""
    output_esdl: str = db.Column(db.String)
    """Output ESDL as string."""
    logs: str = db.Column(db.String)
    """Logs as string."""
