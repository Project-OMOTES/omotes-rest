FROM python:3.12-slim

WORKDIR /app

ENV ENV=dev
ENV FLASK_APP=omotes_rest/main.py

RUN apt-get -y update && \
	apt-get install -y --only-upgrade ca-certificates && \
	apt-get clean
RUN pip install --upgrade 'pip>=26.2.2'

COPY omotes-rest/requirements.txt /app/omotes_rest/requirements.txt
RUN pip install --no-cache-dir -r /app/omotes_rest/requirements.txt

COPY ../omotes-sdk-protocol/python/ /omotes-sdk-protocol/python/
COPY ../omotes-sdk-python/ /omotes-sdk-python/
RUN pip install /omotes-sdk-python/
RUN pip install /omotes-sdk-protocol/python/

COPY omotes-rest/src /app
# To avoid warning from flask dotenv.
RUN touch .env

CMD ["/app/start.sh"]
