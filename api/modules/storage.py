import uuid

from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists,NoSuchKey)
from datetime import timedelta, datetime

from sanic import Blueprint
from sanic.response import json, text, stream
from sanic.exceptions import abort
from sanic_openapi import doc



storage = Blueprint('storage', url_prefix='/storage')

minio_client = None
bucket_name = None

@storage.listener('before_server_start')
def init_minio(app,loop):
    global minio_client
    global bucket_name
    cfg = app.config
    minio_client = Minio(cfg['MINIO_HOST'],access_key=cfg['ACCESS_KEY'],secret_key=cfg['SECRET_KEY'],secure=True)

    # TODO add logging
    try:
        minio_client.make_bucket(cfg['BUCKET_NAME'], location="us-east-1")
    except BucketAlreadyOwnedByYou:
        pass
    except BucketAlreadyExists:
        pass
    except ResponseError:
        raise

    bucket_name = cfg['BUCKET_NAME']

def file_exists(id):
    try:
        minio_client.stat_object(bucket_name, id)
    except NoSuchKey:
        return False
    return True

class PresignedUrl:
    id = doc.String("UUID of requested object")
    url = doc.String("Presigned URL")
    exp = doc.Integer("Expiration in UNIX Time Stamp")

@storage.get("/file/<file_id:uuid>/")
@doc.summary("Creates download url for selected file")
@doc.response(404, {"message": "File not found"}, description="File not found")
@doc.produces(PresignedUrl)
async def get_file(request,file_id):
    file_id = str(file_id)

    if not file_exists(file_id):
        raise abort(404,"File not found")
    try:
        presigned_url = minio_client.presigned_get_object(bucket_name, file_id, expires=timedelta(days=3))
    except NoSuchKey:
        raise abort(404,"File not found")
    
    unix_exp = int((datetime.now()+timedelta(days=3)).timestamp())
    return json({'id':file_id,'url':presigned_url,'exp':unix_exp})


@storage.get("/upload/")
@doc.summary("Creates upload url for a new file")
@doc.produces(PresignedUrl)
async def upload_handler(request):
    filename = str(uuid.uuid4())
    while file_exists(filename):
        filename = str(uuid.uuid4())

    presigned_url = minio_client.presigned_put_object(bucket_name,filename,expires=timedelta(days=3))
    unix_exp = int((datetime.now()+timedelta(days=3)).timestamp())
    return json({'id':filename,'url':presigned_url,'exp':unix_exp})
