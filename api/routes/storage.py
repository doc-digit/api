import uuid

from enum import Enum
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel, UUID4, UrlStr

from minio import Minio
from minio.error import (
    ResponseError,
    BucketAlreadyOwnedByYou,
    BucketAlreadyExists,
    NoSuchKey,
)
from sqlalchemy.orm import Session


from core import config
from api.models import PdfRequest, Page
from api.exceptions import NotFoundException
from api.utils.get_db import get_db
from starlette.responses import JSONResponse

router = APIRouter()


minio_client = Minio(
    config.MINIO_HOST,
    access_key=config.MINIO_ACCESS,
    secret_key=config.MINIO_SECRET,
    secure=config.MINIO_SECURE,
)


def make_bucket(name):
    try:
        minio_client.make_bucket(name, location="us-east-1")
    except BucketAlreadyOwnedByYou:
        pass
    except BucketAlreadyExists:
        pass
    except ResponseError:
        raise


make_bucket(config.BUCKET_NAME_PDF)
make_bucket(config.BUCKET_NAME_SCAN)


def file_exists(id, bucket_name):
    try:
        minio_client.stat_object(bucket_name, id)
    except NoSuchKey:
        return False
    return True


class PresignedUrl(BaseModel):
    id: uuid.UUID
    url: UrlStr
    exp: int


class UploadTypeEnum(str, Enum):
    document = "document"
    page = "page"


class UploadIn(BaseModel):
    parent_id: uuid.UUID
    parent_type: UploadTypeEnum


class UploadInPdf(BaseModel):
    id: uuid.UUID


def get_pdf_by_id(db_session: Session, pdf_request_id: uuid.UUID):
    pdf = (
        db_session.query(PdfRequest)
        .filter(PdfRequest.id == pdf_request_id)
        .filter(PdfRequest.processed == False)
        .first()
    )
    return pdf


def create_page_document(db_session: Session, document_id: uuid.UUID):
    """
    New page with document id
    """
    page = Page(document=document_id)
    db_session.add(page)
    db_session.commit()
    return page.id


def create_page_old(db_session: Session, page_id: uuid.UUID):
    """
    New page with old page data copied
    """
    old_page = (
        db_session.query(Page)
        .filter(Page.id == page_id)
        .filter(Page.processed_page == None)
        .first()
    )
    if not old_page:
        raise NotFoundException
    page = Page(rotation=old_page.rotation, document=old_page.document)
    db_session.add(page)
    db_session.flush()
    old_page.processed_page = page.id

    db_session.commit()
    return page.id


def generate_upload_presigned_url(bucket_name: str, file_id: uuid.UUID):
    file_id = str(file_id)

    presigned_url = minio_client.presigned_put_object(
        bucket_name, file_id, expires=timedelta(days=3)
    )
    unix_exp = int((datetime.now() + timedelta(days=3)).timestamp())

    return {"id": file_id, "url": presigned_url, "exp": unix_exp}


def generate_download_presigned_url(bucket_name: str, file_id: uuid.UUID):
    file_id = str(file_id)

    if not file_exists(file_id, bucket_name):
        raise NotFoundException
    try:
        presigned_url = minio_client.presigned_get_object(
            bucket_name, file_id, expires=timedelta(days=3)
        )
    except NoSuchKey:
        raise NotFoundException

    unix_exp = int((datetime.now() + timedelta(days=3)).timestamp())

    return {"id": file_id, "url": presigned_url, "exp": unix_exp}


@router.get(
    "/file/scan", response_model=PresignedUrl, summary="Create download url for scan"
)
def get_scan(file_id: uuid.UUID):
    """
    Create download url for scan file
    """
    return generate_download_presigned_url(config.BUCKET_NAME_SCAN, file_id)


@router.get(
    "/file/pdf", response_model=PresignedUrl, summary="Create upload url for pdf"
)
def get_pdf(file_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Create download url for pdf 
    """
    return generate_download_presigned_url(config.BUCKET_NAME_PDF, file_id)


@router.post(
    "/upload/scan", response_model=PresignedUrl, summary="Create upload url for scan"
)
def upload_handler(upload: UploadIn, db: Session = Depends(get_db)):
    """
    Create upload url for a new scan
    """

    if upload.parent_type == "document":
        file_id = create_page_document(db, upload.parent_id)

    elif upload.parent_type == "page":
        file_id = create_page_old(db, upload.parent_id)

    else:
        raise NotImplementedError
    return generate_upload_presigned_url(config.BUCKET_NAME_SCAN, file_id)


@router.post(
    "/upload/pdf", response_model=PresignedUrl, summary="Create upload url for pdf"
)
def upload_pdf(upload: UploadInPdf, db: Session = Depends(get_db)):
    """
    Create upload url for a new pdf
    """
    pdf_request = get_pdf_by_id(db, upload.id)
    if not pdf_request:
        raise NotFoundException

    return generate_upload_presigned_url(config.BUCKET_NAME_PDF, pdf_request.id)
