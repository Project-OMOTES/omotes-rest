FROM python:3.10-slim

ENV ENV=prod
ENV FLASK_APP=omotes_rest/main.py

RUN apt-get -y update
RUN pip install --upgrade pip

# Install Python dependencies.
COPY requirements.txt /code/

WORKDIR /code
RUN pip install --no-cache-dir -r requirements.txt

COPY src /code
# To avoid warning from flask dotenv.
RUN touch .env

#RUN #pip install -e .

CMD gunicorn omotes_rest.main:app --config gunicorn.conf.py
#CMD gunicorn omotes_rest.main:app -t 300 -w 1 -b :9200 --pythonpath src
