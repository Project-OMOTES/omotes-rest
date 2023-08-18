from dataclasses import field
from datetime import datetime
from typing import List, Optional, Dict

import marshmallow_dataclass
from marshmallow_dataclass import dataclass
from flask_smorest import Blueprint, abort
# from marshmallow import Schema, fields

from flask.views import MethodView
from tno.shared.log import get_logger

logger = get_logger(__name__)

api = Blueprint("dispatch", "dispatch", url_prefix="/", description="Dispatch an ESDL to an optimizer")

@dataclass
class RequestDispatch:
    name: Optional[str]
    username: str
    energysystem: str
    config: Optional[Dict] = field(metadata=dict(required=False))


@dataclass
class RequestDispatchResponse:
    status: str
    job_id: int


@dataclass
class Job:
    id: int
    name: str
    username: str
    status: str
    timestamp: datetime
    esdl: Optional[str] = field(metadata=dict(required=False))
    log: Optional[str] = field(metadata=dict(required=False))

@dataclass
class JobQueryArgs:
    """
    Username is always required for filtering out the jobs for this user

    id is optional for a specific id to request
    """
    id: Optional[int] = field(metadata=dict(required=False))
    username: str


@dataclass
class LogResponse:
    job_id: int
    log: str


@dataclass
class ESDLResultResponse:
    job_id: int
    esdl: str


# RequestDispatchSchema = marshmallow_dataclass.class_schema(RequestDispatch)()
# RequestDispatchResponseSchema = marshmallow_dataclass.class_schema(RequestDispatchResponse)()
# JobsResponseSchema = marshmallow_dataclass.class_schema(JobsResponse)()


@api.route("/dispatch")
class Dispatch(MethodView):
    @api.arguments(RequestDispatch.Schema())
    @api.response(200, RequestDispatchResponse.Schema())
    def post(self, request: RequestDispatch):
        return RequestDispatchResponse(status="Accepted", job_id=1)


@api.route("/jobs")
class ListJobs(MethodView):
    """
    This endpoint returns the list of jobs for a specific user, ordered by time finished
    """
    @api.arguments(JobQueryArgs.Schema())
    @api.response(200, Job.Schema(many=True))
    def post(self, query: JobQueryArgs):
        print(query)
        # b64 decode ESDL string
        # create job in SDK
        return [Job(username=query.username or "Ewoud", id=query.id or 1234, name="First run", status="RUNNING", timestamp=datetime.now())]
@api.route("/job/<int:id>")
class GetJob(MethodView):
    """
    Returns a specific job
    """
    @api.response(200, Job.Schema(many=False))
    def get(self, job_id: int):
        print(job_id)
        return Job(username="Ewoud", id=job_id, name="First run", status="FINISHED",
                   timestamp=datetime.now())

@api.route("/job/log/<int:id>")
class GetLog(MethodView):
    """
    Returns the logging of the workflow for a specific Job
    """
    @api.response(200, LogResponse.Schema())
    def get(self, job_id: int):
        print(job_id)
        return LogResponse(job_id=job_id, log="This is a log with no errors")

@api.route("/job/result/<int:id>")
class GetESDLResult(MethodView):
    """
    Returns the ESDL result of a specific job, if available
    """
    @api.response(200, ESDLResultResponse.Schema())
    def get(self, job_id: int):
        print(job_id)
        if None:  # check if result is available first
            abort(404, message="Job is not finished. Current state is: Running")
        # b64 encode esdl string
        return ESDLResultResponse(job_id=job_id, esdl="<EnergySystem/>")