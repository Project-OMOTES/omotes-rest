from typing import cast

from flask import current_app as flask_app, Flask

from omotes_rest import RestInterface


class OmotesRestApp(Flask):
    """Type-complete description with extensions of the Flask app."""

    rest_if: RestInterface


current_app = cast(OmotesRestApp, flask_app)
