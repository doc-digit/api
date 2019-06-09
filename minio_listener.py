import pika
import json
import os
from core import config
from loguru import logger
from api.database import db_session
from api.models import Page, PdfRequest
from datetime import datetime
from fastapi.encoders import jsonable_encoder

logger.add("minio_listener.log", rotation="500 MB")

properties = pika.BasicProperties(
    app_id="docdigit-api", content_type="application/json"
)


@logger.catch
def on_message(channel, method_frame, header_frame, body):
    json_body = json.loads(body.decode("utf8"))
    if json_body["EventName"] == "s3:ObjectCreated:Put":
        record = json_body["Records"][0]
        bucket_name = record["s3"]["bucket"]["name"]
        file_name = record["s3"]["object"]["key"].split(".")[0]
        upload_date = datetime.strptime(record["eventTime"], "%Y-%m-%dT%H:%M:%SZ")

        if bucket_name == config.BUCKET_NAME_SCAN:
            page = db_session.query(Page).filter(Page.id == file_name).one()
            page.upload_date = upload_date
            processed_page = (
                db_session.query(Page).filter(Page.processed_page == file_name).first()
            )
            if processed_page is None:
                logger.info(f"Page {file_name} sent to processing.")
                channel.basic_publish(
                    "amq.direct", "new_page", str(jsonable_encoder(page)), properties
                )
        elif bucket_name == config.BUCKET_NAME_PDF:
            pdf = db_session.query(PdfRequest).filter(PdfRequest.id == file_name).one()
            pdf.upload_date = upload_date
        db_session.commit()
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


connection = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
channel = connection.channel()
channel.basic_consume("bucketlogs", on_message)
try:
    logger.info("Listening incoming messages")
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
connection.close()

