import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Generator

from sqlalchemy import select, update, delete, create_engine, orm
from sqlalchemy.orm.strategy_options import load_only
from sqlalchemy.orm import Session as SQLSession
from sqlalchemy.engine import Engine, URL

import logging
from omotes_rest.apis.api_dataclasses import JobRestStatus, JobInput
from omotes_rest.db_models.job_rest import JobRest
from omotes_rest.config import PostgresConfig

logger = logging.getLogger("omotes_rest")

session_factory = orm.sessionmaker()
Session = orm.scoped_session(session_factory)

SELECT_JOB_SUMMARY_STMT = select(JobRest).options(
    load_only(
        JobRest.job_id,
        JobRest.job_name,
        JobRest.workflow_type,
        JobRest.status,
        JobRest.progress_fraction,
        JobRest.registered_at,
        JobRest.running_at,
        JobRest.stopped_at,
        JobRest.user_name,
        JobRest.project_name,
    )
)


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


def initialize_db(application_name: str, config: PostgresConfig) -> Engine:
    """Initialize the database connection by creating the engine.

    Also configure the default session maker.

    :param application_name: Identifier for the connection to the SQL database.
    :param config: Configuration on how to connect to the SQL database.
    """
    logger.info(
        "Connecting to PostgresDB at %s:%s as user %s to db %s",
        config.host,
        config.port,
        config.username,
        config.database,
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
        logger.error(e)

    # Bind the global session to the actual engine.
    Session.configure(bind=engine)

    return engine


class PostgresInterface:
    """Interface to the SQL database for any queries to persist or retrieve job information.

    Note: The interface may be called from many threads at once. Therefor each query/function
    in this interface must set up a Session (scope) separately.
    """

    db_config: PostgresConfig
    """Configuration on how to connect to the database."""
    engine: Engine
    """Engine for starting connections to the database."""

    def __init__(self, postgres_config: PostgresConfig) -> None:
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
        job_input: JobInput,
        job_priority: str,
    ) -> None:
        """Insert a new job into the database.

        Note: Assumption is that the job_id is unique and has not yet been added to the database.

        :param job_id: Unique identifier of the job.
        :param job_input: Received input for the job.
        :param job_input: Received input ESDL for the job.
        """
        with session_scope(do_expunge=False) as session:
            new_job = JobRest(
                job_id=job_id,
                job_name=job_input.job_name,
                workflow_type=job_input.workflow_type,
                job_priority=job_priority,
                status=JobRestStatus.REGISTERED,
                progress_fraction=0,
                progress_message="Job registered.",
                registered_at=datetime.now(),
                timeout_after_s=job_input.timeout_after_s,
                user_name=job_input.user_name,
                project_name=job_input.project_name,
                input_params_dict=job_input.input_params_dict,
                input_esdl=job_input.input_esdl,
            )
            session.add(new_job)
        logger.debug("Job %s is submitted as new job in database", job_id)

    def set_job_registered(self, job_id: uuid.UUID) -> None:
        """Set the status of the job to 'REGISTERED'.

        :param job_id: Job id.
        """
        logger.debug("For job '%s' received new status REGISTERED")

        with session_scope() as session:
            stmnt = (
                update(JobRest)
                .where(JobRest.job_id == job_id)
                .values(status=JobRestStatus.REGISTERED, registered_at=datetime.now())
            )
            session.execute(stmnt)

    def set_job_enqueued(self, job_id: uuid.UUID) -> None:
        """Set the status of the job to 'ENQUEUED'.

        :param job_id: Job id.
        """
        logger.debug("For job '%s' received new status ENQUEUED")

        with session_scope() as session:
            stmnt = (
                update(JobRest)
                .where(JobRest.job_id == job_id)
                .values(status=JobRestStatus.ENQUEUED, submitted_at=datetime.now())
            )
            session.execute(stmnt)

    def set_job_running(self, job_id: uuid.UUID) -> None:
        """Set the status of the job to 'RUNNING'.

        :param job_id: Job id.
        """
        logger.debug("For job '%s' received new status RUNNING")

        with session_scope() as session:
            stmnt = (
                update(JobRest)
                .where(JobRest.job_id == job_id)
                .values(status=JobRestStatus.RUNNING, running_at=datetime.now())
            )
            session.execute(stmnt)

    def set_job_stopped(
        self,
        job_id: uuid.UUID,
        new_status: JobRestStatus,
        logs: str | None = None,
        output_esdl: str | None = None,
        esdl_feedback: dict[str, list] | None = None,
    ) -> None:
        """Set the job to stopped with supplied status.

        :param job_id: Job id.
        :param new_status: JobRestStatus.
        :param logs: optional string containing the job logs.
        :param output_esdl: optional string containing the job output esdl.
        :param esdl_feedback: optional esdl feedback messages per esdl object id.
        """
        logger.debug("For job '%s' received new status '%s'", job_id, new_status)

        with session_scope() as session:
            stmnt = (
                update(JobRest)
                .where(JobRest.job_id == job_id)
                .values(
                    status=new_status,
                    stopped_at=datetime.now(),
                    logs=logs,
                    output_esdl=output_esdl,
                    esdl_feedback=esdl_feedback,
                )
            )
            session.execute(stmnt)

    def set_job_progress(
        self, job_id: uuid.UUID, progress_fraction: float, progress_message: str
    ) -> None:
        """Set the status of the job to RUNNING.

        :param job_id: Job id.
        :param progress_fraction: new progress fraction.
        :param progress_message: new progress message.
        """
        logger.debug(
            "For job '%s' received a new progress '%s' with message '%s'",
            job_id,
            progress_fraction,
            progress_message,
        )
        with session_scope() as session:
            stmnt = (
                update(JobRest)
                .where(JobRest.job_id == job_id)
                .values(progress_fraction=progress_fraction, progress_message=progress_message)
            )
            session.execute(stmnt)

    def get_job_status(self, job_id: uuid.UUID) -> JobRestStatus | None:
        """Retrieve the current job status.

        :param job_id: Job id.
        :return: Current job status.
        """
        logger.debug("Retrieving job status for job with id '%s'", job_id)
        with session_scope(do_expunge=True) as session:
            stmnt = select(JobRest.status).where(JobRest.job_id == job_id)
            job_status = session.scalar(stmnt)
        return job_status

    def get_job(self, job_id: uuid.UUID) -> JobRest | None:
        """Retrieve the job info from the database.

        :param job_id: Job id.
        :return: Job if it is available in the database.
        """
        logger.debug("Retrieving job data for job with id '%s'", job_id)
        with session_scope(do_expunge=True) as session:
            stmnt = select(JobRest).where(JobRest.job_id == job_id)
            job = session.scalar(stmnt)
        return job

    def delete_job(self, job_id: uuid.UUID) -> bool:
        """Remove the job from the database.

        :param job_id: Job id.
        :return: True if the job was removed or False if the job was not in the database.
        """
        logger.debug("Deleting job with id '%s'", job_id)

        job_to_delete = self.get_job(job_id)
        with session_scope() as session:
            if job_to_delete:
                stmnt = delete(JobRest).where(JobRest.job_id == job_id)
                session.execute(stmnt)
                job_deleted = True
            else:
                job_deleted = False

        return job_deleted

    def get_jobs(self, job_ids: list[uuid.UUID] | None = None) -> list[JobRest]:
        """Retrieve a list of the jobs.

        :param job_ids: Optional list of uuid's to select specific jobs, default is all jobs.
        :return: List of jobs.
        """
        with session_scope(do_expunge=True) as session:
            stmnt = SELECT_JOB_SUMMARY_STMT
            if job_ids:
                logger.debug(
                    f"Retrieving job data for jobs "
                    f"'{','.join([str(job_id) for job_id in job_ids])}'"
                )
                stmnt = stmnt.where(JobRest.job_id.in_(job_ids))
            else:
                logger.debug("Retrieving job data for all jobs")

            jobs = list(session.scalars(stmnt).all())
        return jobs

    def get_job_output_esdl(self, job_id: uuid.UUID) -> str | None:
        """Retrieve the output ESDL of a job.

        :param job_id: Job id.
        :return: Output ESDL as a base64 string.
        """
        logger.debug("Retrieving job output esdl for job with id '%s'", job_id)
        with session_scope() as session:
            stmnt = select(JobRest.output_esdl).where(JobRest.job_id == job_id)
            job_output_esdl: str | None = session.scalar(stmnt)
        return job_output_esdl

    def get_job_logs(self, job_id: uuid.UUID) -> str | None:
        """Retrieve the logs of a job.

        :param job_id: Job id.
        :return: Job logs as a string.
        """
        logger.debug("Retrieving job log for job with id '%s'", job_id)
        with session_scope() as session:
            stmnt = select(JobRest.logs).where(JobRest.job_id == job_id)
            job_logs: str | None = session.scalar(stmnt)
        return job_logs

    def get_jobs_from_user(self, user_name: str) -> list[JobRest]:
        """Retrieve a list of the jobs from a specific user.

        :param user_name: Name of the user.
        :return: List of jobs.
        """
        logger.debug(f"Retrieving job data for jobs from user '{user_name}'")
        with session_scope(do_expunge=True) as session:
            stmnt = SELECT_JOB_SUMMARY_STMT.where(JobRest.user_name == user_name)
            jobs = list(session.scalars(stmnt).all())
        return jobs

    def get_jobs_from_project(self, project_name: str) -> list[JobRest]:
        """Retrieve a list of the jobs from a specific project.

        :param project_name: Name of the project.
        :return: List of jobs.
        """
        logger.debug(f"Retrieving job data for jobs from project '{project_name}'")
        with session_scope(do_expunge=True) as session:
            stmnt = SELECT_JOB_SUMMARY_STMT.where(JobRest.project_name == project_name)
            jobs = list(session.scalars(stmnt).all())
        return jobs
