FROM python:3.12-slim

WORKDIR /app

ENV ENV=prod
ENV FLASK_APP=omotes_rest/main.py

RUN apt-get -y update
RUN pip install --upgrade pip

COPY requirements.txt /app/omotes_rest/requirements.txt
RUN pip install --no-cache-dir -r /app/omotes_rest/requirements.txt

COPY src /app
# To avoid warning from flask dotenv.
RUN touch .env

CMD ["/app/start.sh"]
