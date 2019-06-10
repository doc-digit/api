FROM python:3.7

WORKDIR /api

COPY . /api

RUN pip install pipenv
RUN pipenv install --system --deploy
RUN chmod +x run.sh

EXPOSE 8080

CMD ["./run.sh"]

