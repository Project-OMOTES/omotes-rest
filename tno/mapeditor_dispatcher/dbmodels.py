import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NwnJob(Base):
    __tablename__ = "nwnjob"

    job_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    project_name = db.Column(db.String, nullable=False)
