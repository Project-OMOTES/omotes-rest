from dataclasses import field
from datetime import datetime
from typing import List, Optional

import marshmallow_dataclass
from marshmallow_dataclass import dataclass
from flask_smorest import Blueprint
# from marshmallow import Schema, fields

from flask.views import MethodView
from tno.shared.log import get_logger

logger = get_logger(__name__)

api = Blueprint("dispatch", "dispatch", url_prefix="/", description="Dispatch an ESDL to an optimizer")


# class UserSchema(SQLAlchemySchema):
#     class Meta:
#         model = User
#         load_instance: True
#
#     id = auto_field()
#     name = auto_field()
#
#
# class UserListSchema(Schema):
#     users = fields.Nested(UserSchema, many=True)

@dataclass
class RequestDispatch:
    name: str
    username: str
    esdl: str
    config: dict


@dataclass
class RequestDispatchResponse:
    status: str


@dataclass
class Jobs:
    id: int
    name: str
    username: str
    status: str
    timestamp: datetime

@dataclass
class JobsQueryArgs:
    id: Optional[int] = field(metadata=dict(required=False))
    username: Optional[str] = field(metadata=dict(required=False))


# @dataclass
# class JobsResponse:
#     jobs: List[Jobs]


# RequestDispatchSchema = marshmallow_dataclass.class_schema(RequestDispatch)()
# RequestDispatchResponseSchema = marshmallow_dataclass.class_schema(RequestDispatchResponse)()
# JobsResponseSchema = marshmallow_dataclass.class_schema(JobsResponse)()


@api.route("/dispatch")
class Dispatch(MethodView):
    @api.arguments(RequestDispatch.Schema())
    @api.response(200, RequestDispatchResponse.Schema())
    def post(self, request: RequestDispatch):
        return RequestDispatchResponse(request.name)


@api.route("/jobs")
class ListJobs(MethodView):
    @api.arguments(JobsQueryArgs.Schema())
    @api.response(200, Jobs.Schema(many=True))
    def post(self, query: JobsQueryArgs):
        print(query)
        return [Jobs(username="Test", id=1, name="First run", status="RUNNING", timestamp=datetime.now())]
