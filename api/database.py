import uuid

# from gino.ext.sanic import Gino

from sqlalchemy.dialects import postgresql

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core import config
from api.models import Base

engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

db_session = SessionLocal()
