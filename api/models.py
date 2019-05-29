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
from sqlalchemy.dialects.postgresql import UUID


class CustomBase:
    @declared_attr
    def __tablename__(self, cls):
        return cls.__name__.lower()


Base = declarative_base(cls=CustomBase)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    pin = Column(Integer)
    name = Column(String)


class DocumentType(Base):
    __tablename__ = "document_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    # TODO


class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    user = Column(ForeignKey("users.id"))
    # not foreign key because student will be obtained from different api
    student = Column(Integer)

    document_type = Column(ForeignKey("document_types.id"))

    def __repr__(self):
        return "Document {}".format(self.id)


class Page(Base):
    __tablename__ = "pages"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    rotation = Column(SmallInteger, default=0)

    document = Column(ForeignKey("documents.id"))

    def __repr__(self):
        return "Page {} Document {}".format(self.id, self.document_id)


class PdfRequest(Base):
    __tablename__ = "pdf_requests"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    document = Column(ForeignKey("documents.id"))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    page_order = Column(String)
    status = Column(SmallInteger)


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    surname = Column(String)
    album_id = Column(Integer)
    semester = Column(Integer)
    course_name = Column(String)
    faculty = Column(String)
