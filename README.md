# Doc-digit api

Main purpose of having this is to allow client to interact with file storage, processing server and more (its just a quick draft).

Python3.7, FastAPI, Pytest for testing.

## How to

Install:

```
pipenv install --dev
```

Run:

```
pipenv shell
uvicorn api.main:app --reload
```

Docs available at http://0.0.0.0:8000/docs

Test:

```
pipenv shell
python -m pytest
```

# Api parts

Api is divided to parts, that do things.

## Storage adapter

For now we use Minio as a storage system. However it may always change, thats the main reason we build adapter.

Although Minio is nice, we found that some features that we need are missing. That's what adapter will take care of too.

### Draft of client flow:

- client uploads file (possibly photo), adapter (server returns file key) -oauth 2 authorization code grant PKCE
- adapter uploads file to storage (now minio), after upload is complete adapter adds a task to a rabbitmq. Processing microservice
- gets task from rabbitmq, then do processing and send a file to adapter
- adapter uploads file to storage (now minio) and sends info to client (sse or sth idk now)3. Pdf is produced by server.
- server send file to adapter, adapter uploads pdf to different bucket,
- when requested adapter sends pdfs and gets sharing url from storage (now minio )

## Minio listener

There is a need to run minio_listener.py in order to handle minio upload notifications.

```
pipenv shell
python minio_listener.py
```

Bindings for rabbitmq:

```json
"bindings":[

    {
        "source":"amq.direct",
        "vhost":"/",
        "destination":"new_page",
        "destination_type":"queue",
        "routing_key":"new_page",
        "arguments":{
        }
    },
    {
        "source":"bucketevents",
        "vhost":"/",
        "destination":"bucketlogs",
        "destination_type":"queue",
        "routing_key":"bucketlogs",
        "arguments":{
        }
    }

]
```
