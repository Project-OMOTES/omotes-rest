import uuid
from contextlib import contextmanager
from datetime import datetime
import logging
from typing import Generator, Optional

from omotes_sdk_protocol.job_pb2 import JobResult
from sqlalchemy import select, update, delete, create_engine, orm
from sqlalchemy.orm import Session as SQLSession
from sqlalchemy.engine import Engine, URL

from omotes_rest.apis.api_dataclasses import JobRestStatus, JobInput
from omotes_rest.db_models.job_rest import JobRest
from omotes_rest.config import PostgreSQLConfig

LOGGER = logging.getLogger("omotes_rest")

session_factory = orm.sessionmaker()
Session = orm.scoped_session(session_factory)


@contextmanager
def session_scope(do_expunge: bool = False) -> Generator[SQLSession, None, None]:
    """Provide a transactional scope around a series of operations.

    Ensures that the session is committed and closed. Exceptions raised within the 'with' block
    using this contextmanager should be handled in the with block itself. They will not be caught
    by the 'except' here.

    :param do_expunge: Expunge the records cached in this session. Set this to True for SELECT
        queries and keep it False for INSERTS or UPDATES.
    :return: A single SQL session.
    """
    try:
        yield Session()

        if do_expunge:
            Session.expunge_all()
        Session.commit()
    except Exception as e:
        # Only the exceptions raised by session.commit above are caught here
        Session.rollback()
        raise e
    finally:
        Session.remove()


def initialize_db(application_name: str, config: PostgreSQLConfig) -> Engine:
    """Initialize the database connection by creating the engine.

    Also configure the default session maker.

    :param application_name: Identifier for the connection to the SQL database.
    :param config: Configuration on how to connect to the SQL database.
    """
    LOGGER.info(
        "Connecting to PostgresDB at %s:%s as user %s to db %s", config.host, config.port,
        config.username, config.database
    )

    try:
        url = URL.create(
            "postgresql+psycopg2",
            username=config.username,
            password=config.password,
            host=config.host,
            port=config.port,
            database=config.database,
        )

        engine = create_engine(
            url,
            pool_size=20,
            max_overflow=5,
            echo=False,
            connect_args={
                "application_name": application_name,
                "options": "-c lock_timeout=30000 -c statement_timeout=300000",  # 5 minutes
            },
        )
    except Exception as e:
        LOGGER.error(e)

    # Bind the global session to the actual engine.
    Session.configure(bind=engine)

    return engine


class PostgresInterface:
    """Interface to the SQL database for any queries to persist or retrieve job information.

    Note: The interface may be called from many threads at once. Therefor each query/function
    in this interface must set up a Session (scope) separately.
    """

    db_config: PostgreSQLConfig
    """Configuration on how to connect to the database."""
    engine: Engine
    """Engine for starting connections to the database."""

    def __init__(self, postgres_config: PostgreSQLConfig) -> None:
        """Create the PostgreSQL interface."""
        self.db_config = postgres_config

    def start(self) -> None:
        """Start the interface and connect to the database."""
        self.engine = initialize_db("omotes_rest", self.db_config)

    def stop(self) -> None:
        """Stop the interface and dispose of any connections."""
        if self.engine:
            self.engine.dispose()

    def put_new_job(
            self,
            job_id: uuid.UUID,
            job_input: JobInput
    ) -> None:
        """Insert a new job into the database.

        Note: Assumption is that the job_id is unique and has not yet been added to the database.

        :param job_id: Unique identifier of the job.
        :param job_input: Received input for the job
        """
        with session_scope(do_expunge=False) as session:
            new_job = JobRest(
                job_id=job_id,
                job_name=job_input.job_name,
                work_flow_name=job_input.work_flow_name,
                status=JobRestStatus.REGISTERED,
                progress_fraction=0,
                progress_message="Job registered.",
                registered_at=datetime.now(),
                timeout_after_s=job_input.timeout_after_s,
                user_name=job_input.user_name,
                project_name=job_input.project_name,
                input_params_dict_str=job_input.input_params_dict_str,
                input_esdl=job_input.input_esdl
            )
            session.add(new_job)
        LOGGER.debug("Job %s is submitted as new job in database", job_id)

    def set_job_status(self, job_id: uuid.UUID, new_status: int, result: JobResult = None) -> None:
        """Set the status of the job to SUBMITTED.

        :param job_id: Job to set the status to SUBMITTED.
        :param new_status: new status 'int' identifier from protobuf message.
        :param result: optional result containing the result type, logs and output esdl.
        """
        LOGGER.debug("For job '%s' received new status '%s'", job_id, new_status)

        with session_scope() as session:
            if new_status == 0:  # REGISTERED
                stmnt = (
                    update(JobRest)
                    .where(JobRest.job_id == job_id)
                    .values(
                        status=JobRestStatus.REGISTERED, registered_at=datetime.now()
                    )
                )
            elif new_status == 1:  # ENQUEUED
                stmnt = (
                    update(JobRest)
                    .where(JobRest.job_id == job_id)
                    .values(
                        status=JobRestStatus.ENQUEUED, submitted_at=datetime.now()
                    )
                )
            elif new_status == 2:  # RUNNING
                stmnt = (
                    update(JobRest)
                    .where(JobRest.job_id == job_id)
                    .values(
                        status=JobRestStatus.RUNNING, running_at=datetime.now()
                    )
                )
            elif new_status == 3 or new_status == 4:  # FINISHED or CANCELLED
                if result is None:  # Should this happen?
                    final_status = JobRestStatus.ERROR
                elif result.result_type == 0:  # SUCCEEDED
                    final_status = JobRestStatus.SUCCEEDED
                elif result.result_type == 1:  # TIMEOUT
                    final_status = JobRestStatus.TIMEOUT
                elif result.result_type == 2:  # ERROR
                    final_status = JobRestStatus.ERROR
                elif result.result_type == 3:  # CANCELLED
                    final_status = JobRestStatus.CANCELLED

                if result:
                    stmnt = (
                        update(JobRest)
                        .where(JobRest.job_id == job_id)
                        .values(
                            status=final_status, stopped_at=datetime.now(), logs=result.logs,
                            output_esdl=result.output_esdl
                        )
                    )
                else:
                    stmnt = (
                        update(JobRest)
                        .where(JobRest.job_id == job_id)
                        .values(
                            status=final_status, stopped_at=datetime.now()
                        )
                    )
            session.execute(stmnt)

        if result_type:
            if new_status == 3 and result_type == 0:
                self.set_job_progress(job_id, 1, "Job finished successfully.")

    def set_job_progress(self, job_id: uuid.UUID, progress_fraction: float,
                         progress_message: str) -> None:
        """Set the status of the job to RUNNING.

        :param job_id: Job to set the status to RUNNING.
        :param progress_fraction: new progress fraction.
        :param progress_message: new progress message.
        """
        LOGGER.debug("For job '%s' received a new progress '%s' with message '%s'",
                     job_id, progress_fraction, progress_message)
        with session_scope() as session:
            stmnt = (
                update(JobRest)
                .where(JobRest.job_id == job_id)
                .values(
                    progress_fraction=progress_fraction, progress_message=progress_message
                )
            )
            session.execute(stmnt)

    def get_job_status(self, job_id: uuid.UUID) -> Optional[JobRestStatus]:
        """Retrieve the current job status.

        :param job_id: Job to retrieve the status for.
        :return: Current job status.
        """
        LOGGER.debug("Retrieving job status for job with id '%s'", job_id)
        with session_scope(do_expunge=True) as session:
            stmnt = select(JobRest.status).where(JobRest.job_id == job_id)
            job_status = session.scalar(stmnt)
        return job_status

    def get_job(self, job_id: uuid.UUID) -> Optional[JobRest]:
        """Retrieve the job info from the database.

        :param job_id: Job to retrieve the job information for.
        :return: Job if it is available in the database.
        """
        LOGGER.debug("Retrieving job data for job with id '%s'", job_id)
        with session_scope(do_expunge=True) as session:
            stmnt = select(JobRest).where(JobRest.job_id == job_id)
            job = session.scalar(stmnt)
        return job

    def delete_job(self, job_id: uuid.UUID) -> Optional[JobRest]:
        """Remove the job from the database.

        :param job_id: Job to remove from the database.
        :return: True if the job was removed or False if the job was not in the database.
        """
        LOGGER.debug("Deleting job with id '%s'", job_id)
        with session_scope() as session:
            job_to_deleted = self.get_job(job_id)
            if job_to_deleted:
                stmnt = delete(JobRest).where(JobRest.job_id == job_id)
                session.execute(stmnt)

        return job_to_deleted
