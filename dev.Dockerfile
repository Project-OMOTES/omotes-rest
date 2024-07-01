FROM python:3.10-slim

WORKDIR /app

ENV ENV=prod
ENV FLASK_APP=omotes_rest/main.py

RUN apt-get -y update
RUN pip install --upgrade pip

COPY omotes-rest/requirements.txt /app/omotes_rest/requirements.txt
RUN pip install --no-cache-dir -r /app/omotes_rest/requirements.txt

COPY ../omotes-sdk-protocol/python/ /omotes-sdk-protocol/python/
COPY ../omotes-sdk-python/ /omotes-sdk-python/
RUN pip install -e /omotes-sdk-python/
RUN pip install -e /omotes-sdk-protocol/python/

COPY omotes-rest/src /app
# To avoid warning from flask dotenv.
RUN touch .env

CMD gunicorn omotes_rest.main:app --config gunicorn.conf.py
