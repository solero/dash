FROM python:3-alpine

RUN apk add \
    openssl \
    build-base \
    openssl-dev \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    redis \
    postgresql-client

WORKDIR /usr/src/dash

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python", "./bootstrap.py" ]