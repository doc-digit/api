import uuid

from enum import Enum
from datetime import timedelta, datetime
from fastapi import APIRouter
from pydantic import BaseModel, UUID4, UrlStr

from minio import Minio
from minio.error import (
    ResponseError,
    BucketAlreadyOwnedByYou,
    BucketAlreadyExists,
    NoSuchKey,
)

from core import config
from api.exceptions import NotFoundException

router = APIRouter()


minio_client = Minio(
    config.MINIO_HOST,
    access_key=config.MINIO_ACCESS,
    secret_key=config.MINIO_SECRET,
    secure=True,
)

# TODO add loggingmodules
try:
    minio_client.make_bucket(config.BUCKET_NAME, location="us-east-1")
except BucketAlreadyOwnedByYou:
    pass
except BucketAlreadyExists:
    pass
except ResponseError:
    raise

bucket_name = config.BUCKET_NAME


def file_exists(id):
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
    scan = "scan"


class UploadIn(BaseModel):
    parent_id: uuid.UUID
    parent_type: UploadTypeEnum


@router.get("/file/scan", response_model=PresignedUrl)
def get_scan(file_id: uuid.UUID):
    """
    Create download url for scan file
    """
    file_id = str(file_id)

    if not file_exists(file_id):
        raise NotFoundException
    try:
        presigned_url = minio_client.presigned_get_object(
            bucket_name, file_id, expires=timedelta(days=3)
        )
    except NoSuchKey:
        raise NotFoundException

    unix_exp = int((datetime.now() + timedelta(days=3)).timestamp())

    return {"id": file_id, "url": presigned_url, "exp": unix_exp}


@router.get("/file/pdf", response_model=PresignedUrl)
def get_pdf(file_id: uuid.UUID):
    """
    Create download url for pdf 
    """
    pass


@router.get("/upload", response_model=PresignedUrl, summary="Create upload url")
def upload_handler(upload: UploadIn):
    """
    Create upload url for a new file
    """
    file_id = str(uuid.uuid4())

    while file_exists(file_id):
        file_id = str(uuid.uuid4())

    presigned_url = minio_client.presigned_put_object(
        bucket_name, file_id, expires=timedelta(days=3)
    )
    unix_exp = int((datetime.now() + timedelta(days=3)).timestamp())

    return {"id": file_id, "url": presigned_url, "exp": unix_exp}
