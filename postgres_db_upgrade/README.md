
# How to work with alembic to make database revisions
The following commands should be run from this folder. (`cd postgres_db_upgrade`)

- Setup the virtual environment: `./scripts/create_venv.sh`
- Start postgres in setup mode to expose the port to the host: `./scripts/start_postgres_in_setup_mode.sh`
- Make a revision: `alembic revision --autogenerate -m "<some message>"`
- Perform all revisions: `alembic upgrade head`
- Downgrade to a revision: `alembic downgrade <revision>` #(revision='base' to undo everything.)
