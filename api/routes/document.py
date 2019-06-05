import uuid

from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from api.models import DocumentType, PdfRequest, Document, Page


from api.routes.storage import generate_download_presigned_url
from api.utils.get_db import get_db
from api.exceptions import NotFoundException
from core.background_tasks import task_generate_pdf
from core import config

router = APIRouter()


class PageOut(BaseModel):
    id: uuid.UUID
    created_date: datetime
    rotation: int = None
    processed: bool = False
    url: str = ""

    @validator("url", always=True)
    def set_url(cls, v, values):
        if "id" in values:
            return generate_download_presigned_url(
                config.BUCKET_NAME_SCAN, str(values["id"])
            )["url"]
        else:
            return ""


class DocumentIn(BaseModel):
    user: int
    student: int
    document_type: int = None


class DocumentModify(BaseModel):
    user: int = None
    student: int = None
    document_type: int = None


class DocumentOut(DocumentIn):
    id: uuid.UUID
    created_date: datetime


class DocumentPdf(BaseModel):
    document: uuid.UUID
    page_order: List[uuid.UUID]


class DocumentTypeOut(BaseModel):
    id: int
    name: str
    # TODO -> check db model


class DocumentStatus(DocumentOut):
    # not sure about using this (db need to be changed)
    # selected_student_id: int = None
    # detected_student_id: int = None
    # selected_type: DocumentTypeOut = None
    # detected_type: DocumentTypeOut = None
    pages: List[PageOut] = []


def add_document(db_session: Session, document: DocumentIn):
    document = Document(**document.dict())
    db_session.add(document)
    db_session.commit()
    document.id = document.id  # get fields workaround
    return document


def update_document(
    db_session: Session, document_id: uuid.UUID, document: DocumentModify
):
    db_document = db_session.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        raise NotFoundException

    for key, val in document.dict(skip_defaults=True).items():
        setattr(db_document, key, val)
    try:
        db_session.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db_document.id = db_document.id
    return db_document


def get_user_documents(db_session: Session, user_id: int):
    return db_session.query(Document).filter(user_id == user_id).all()


def get_document_status(db_session: Session, document_id: uuid.UUID):
    document = db_session.query(Document).filter(Document.id == document_id).first()
    pages = db_session.query(Page).filter(Page.document == document_id).all()

    setattr(document, "pages", pages)
    return document


def add_create_pdf(db_session: Session, document_pdf: DocumentPdf):
    create_pdf = PdfRequest(**document_pdf.dict())
    db_session.add(create_pdf)
    db_session.commit()
    return create_pdf.id


def get_document_types(db_session: Session):
    return db_session.query(DocumentType).all()


@router.post("/", response_model=DocumentOut)
def create_document(document: DocumentIn, db: Session = Depends(get_db)):
    """
    Create a new document 
    """
    return add_document(db, document)


@router.put("/{document_id}", response_model=DocumentOut)
def modify_document(
    document_id: uuid.UUID, document: DocumentModify, db: Session = Depends(get_db)
):
    """
    Modify a document 
    """
    return update_document(db, document_id, document)


@router.get("/list", response_model=List[DocumentOut])
def list_user_documents(user_id: int, db: Session = Depends(get_db)):
    """
    List users documents
    """
    return get_user_documents(db, user_id)


@router.get("/status", response_model=DocumentStatus)
def document_status(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Check document processing status 
    """
    document_status = get_document_status(db, document_id)
    return document_status


@router.post("/create_pdf")
def create_pdf(
    pdf_request: DocumentPdf,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Submit pdf creation
    """
    pdf_id = add_create_pdf(db, pdf_request)
    pdf_request_dict = pdf_request.dict()
    pdf_request_dict["id"] = pdf_id
    background_tasks.add_task(task_generate_pdf, pdf_request_dict)

    return {"id": pdf_id}


@router.get("/types", response_model=List[DocumentTypeOut])
def document_types(db: Session = Depends(get_db)):
    """
    List available document types
    """
    return get_document_types(db)
