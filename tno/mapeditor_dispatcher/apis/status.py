from flask_smorest import Blueprint
from flask.views import MethodView
from tno.shared.log import get_logger

logger = get_logger(__name__)

api = Blueprint("status", "status", url_prefix="/status")


@api.route("/")
class Status(MethodView):
    def get(self):
        return "OK", 200
