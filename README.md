# Omotes REST service

This webservice allows the MapEditor to call the Omotes SDK to submit new workflow jobs, see their
status and retrieve
the results.

The webservice is based on TNOs Flask REST API Template.

## Usage

Copy `.env.template` to `.env` and fill with the appropriate values.  
To set up the components (for windows run in `Git Bash`):

```bash
./scripts/setup.sh
```

To start the components:

```bash
./scripts/start.sh
```

To stop the components:

```bash
./scripts/stop.sh
```

### Optional start with local code and exposed postgres (dev mode)

There is a dev mode for start which will use the local code for `omotes-rest`, `omotes-sdk-python`
and `omotes-sdk-protocol` (assuming the repos are all in the same folder as this `omotes-rest`
repo), instead of released docker images, and it will expose the postgres port:

```bash
./scripts/start-dev.sh
```

# Directory structure

The following directory structure is used:

- `ci/`: Contains all CI & other development scripts to help standardize the development workflow
  for Linux.
- `config/`: Contains orchestrator workflow definitions configuration. The `workflow_config.json`
  file will be overwritten by a volume mount when deploying via docker.
- `scripts/`: Setup, start en stop scripts.
- `src/`: Source code for omotes-rest.
- `unit_test/`: All unit tests for omotes-rest.
- `.dockerignore`: Contains all files and directories which should not be available while building
  the docker image.
- `.env.template`: Template `.env` file to run the orchestrator locally outside of docker.
- `.gitignore`: Contains all files and directories which are not kept in Git source control.
- `dev-requirements.txt`: Pinned versions of all development and non-development dependencies.
- `Dockerfile`: The build instructions for building the docker image.
- `dev.Dockerfile`: Used when running or testing with local code from the `omotes-system`
  repository.
- `pyproject.toml`: The Python project (meta) information.
- `requirements.txt`: Pinned versions of all dependencies needed to run the orchestrator.

# Development workflow

The scripts under `ci/` are used to standardize the development proces.

- `create_venv`: Creates a local virtual environment (`.venv/`) in which all dependencies may be
  installed.
- `install_dependencies`: Installs all development and non-development dependencies in the local
  virtual environment.
- `lint`: Run the `flake8` to check for linting issues.
- `test_unit`: Run all unit tests under `unit_test/` using `pytest`.
- `typecheck`: Run `mypy` to check the type annotations and look for typing issues.
- `update_dependencies`: Update `dev-requirements.txt` and `requirements.txt` based on the
  dependencies specified in `pyproject.toml`

A typical development workflow would be:

1. create and configure `.env` from `.env.template`
2. run `create_venv`
3. run `install_dependencies`.
4. develop or update the codebase according to the requirements...
5. run `lint`, `test_unit`, and `typecheck` to check for code quality issues.

All these scripts are expected to run from the root of the repository.

## How to work with alembic to make database revisions

First set up the development environment with `create_venv` and `install_dependencies`. Then you
can make the necessary changes to `src/omotes-rest/db_models/`. Finally, a new SQL schema
revision may be generated using `alembic` by running:
```bash
./scripts/db_models_generate_new_revision.sh "revision message"
```

All database revisions will be automatically applied when omotes-rest is started.

## Direct Alembic control

In case more control is necessary, you can run the necessary alembic commands directly after
activating the virtual environment.

First, change directory: `cd src/`

- Make a revision: `alembic revision --autogenerate -m "<some message>"`
- Perform all revisions: `alembic upgrade head`
- Downgrade to a revision: `alembic downgrade <revision>` (revision 'base' to
  undo everything.)

## Monitoring job runs

A SQL script can be applied optionally to monitor omotes job runs. More details see [Monitoring_job_runs](/doc/Monitoring_job_runs.md)
