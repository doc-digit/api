#!/bin/sh

uvicorn api.main:app --host 0.0.0.0 &
python minio_listener.py &
disown
