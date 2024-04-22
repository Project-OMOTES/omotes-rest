import os


class POSTGRESConfig:
    """Retrieve POSTGRES configuration from environment variables."""

    host: str
    port: int
    database: str
    username: str | None
    password: str | None

    def __init__(self, prefix: str = ""):
        """Create the POSTGRES configuration and retrieve values from env vars.

        :param prefix: Prefix to the name environment variables.
        """
        self.host = os.environ.get(f"{prefix}POSTGRES_HOST", "localhost")
        self.port = int(os.environ.get(f"{prefix}POSTGRES_PORT", "5432"))
        self.database = os.environ.get(f"{prefix}POSTGRES_DATABASE", "public")
        self.username = os.environ.get(f"{prefix}POSTGRES_USERNAME")
        self.password = os.environ.get(f"{prefix}POSTGRES_PASSWORD")
