import os


class PostgreSQLConfig:
    """Retrieve PostgreSQL configuration from environment variables."""

    host: str
    port: int
    database: str
    username: str | None
    password: str | None

    def __init__(self, prefix: str = ""):
        """Create the PostgreSQL configuration and retrieve values from env vars.

        :param prefix: Prefix to the name environment variables.
        """
        self.host = os.environ.get(f"{prefix}POSTGRESQL_HOST", "localhost")
        self.port = int(os.environ.get(f"{prefix}POSTGRESQL_PORT", "5432"))
        self.database = os.environ.get(f"{prefix}POSTGRESQL_DATABASE", "public")
        self.username = os.environ.get(f"{prefix}POSTGRESQL_USERNAME")
        self.password = os.environ.get(f"{prefix}POSTGRESQL_PASSWORD")
