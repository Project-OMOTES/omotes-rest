FROM python:3.10-slim

ENV ENV=prod
ENV FLASK_APP=tno/mapeditor_dispatcher/main.py

RUN apt-get -y update
RUN pip install --upgrade pip

# Install Python dependencies.
COPY requirements.txt /code/

WORKDIR /code
# To avoid warning from flask dotenv.
RUN touch .env
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code

RUN pip install -e .

CMD gunicorn --preload tno.mapeditor_dispatcher.main:app -t 300 -w 1 -b :9200
