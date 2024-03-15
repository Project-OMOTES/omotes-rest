from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, orm
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session as SQLSession

from src.omotes_rest.settings import EnvSettings
from omotes_rest.log import get_logger

logger = get_logger("omotes_rest")

session_factory = orm.sessionmaker()
Session = orm.scoped_session(session_factory)


@contextmanager
def session_scope(bind=None) -> Generator[SQLSession, None, None]:
    """Provide a transactional scope around a series of operations. Ensures that the session is
    committed and closed. Exceptions raised within the 'with' block using this contextmanager
    should be handled in the with block itself. They will not be caught by the 'except' here."""
    try:
        if bind:
            yield Session(bind=bind)
        yield Session()
        Session.commit()
    except Exception:
        # Only the exceptions raised by session.commit above are caught here
        Session.rollback()
        raise
    finally:
        Session.remove()


def initialize_db(application_name: str):
    """
    Initialize the database connection by creating the engine and configuring
    the default session maker.
    """
    logger.info(
        "Connecting to PostgresDB at %s:%s as user %s",
        EnvSettings.postgis_host(),
        EnvSettings.postgis_port(),
        EnvSettings.postgis_user(),
    )
    url = URL.create(
        "postgresql+psycopg2",
        username=EnvSettings.postgis_user(),
        password=EnvSettings.postgis_password(),
        host=EnvSettings.postgis_host(),
        port=EnvSettings.postgis_port(),
        database=EnvSettings.postgis_database_name(),
    )

    engine = create_engine(
        url,
        pool_size=20,
        max_overflow=5,
        echo=True,
        connect_args={
            "application_name": application_name,
            "options": "-c lock_timeout=30000 -c statement_timeout=300000",  # 5 minutes
        },
    )

    # Bind the global session to the actual engine.
    Session.configure(bind=engine)

    return engine
