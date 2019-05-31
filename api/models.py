import uuid
import datetime
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    SmallInteger,
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.dialects.postgresql import UUID, ARRAY


class CustomBase:
    @declared_attr
    def __tablename__(self, cls):
        return cls.__name__.lower()


Base = declarative_base(cls=CustomBase)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    pin = Column(Integer, nullable=False)
    name = Column(String, nullable=False)


class DocumentType(Base):
    __tablename__ = "document_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # TODO


class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    user = Column(ForeignKey("users.id"), nullable=False)
    # not foreign key because student will be obtained from different api
    student = Column(Integer, nullable=False)

    document_type = Column(ForeignKey("document_types.id"))


class Page(Base):
    __tablename__ = "pages"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    upload_date = Column(DateTime)
    rotation = Column(SmallInteger, default=0)

    processed_page = Column(ForeignKey("pages.id"))
    document = Column(ForeignKey("documents.id"), nullable=False)

    def __repr__(self):
        return "Page {} Document {}".format(self.id, self.document_id)


class PdfRequest(Base):
    __tablename__ = "pdf_requests"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    document = Column(ForeignKey("documents.id"), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    upload_date = Column(DateTime)

    page_order = Column(ARRAY(UUID))
    processed = Column(Boolean, default=False)


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    surname = Column(String)
    album_id = Column(Integer)
    semester = Column(Integer)
    course_name = Column(String)
    faculty = Column(String)
