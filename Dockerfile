FROM python:3.7

WORKDIR /api

COPY . /api

RUN pip install pipenv
RUN pipenv install --system --deploy

EXPOSE 8080

CMD ["uvicorn", "api.main:app"]

