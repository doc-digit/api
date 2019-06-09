import pika
from fastapi.encoders import jsonable_encoder
from core import config

connection = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(queue="generate_pdf")


def task_generate_pdf(pdf_request_dict):
    properties = pika.BasicProperties(
        app_id="docdigit-api", content_type="application/json"
    )

    channel.basic_publish(
        "", "generate_pdf", str(jsonable_encoder(pdf_request_dict)), properties
    )


""" may be not needed
def task_page(page):
    properties = pika.BasicProperties(
        app_id="docdigit-api", content_type="application/json"
    )

    channel.basic_publish("", "new_page", str(jsonable_encoder(page)), properties)
"""
