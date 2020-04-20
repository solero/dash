FROM python:3-alpine

RUN apk add build-base openssl-dev libffi-dev jpeg-dev zlib-dev

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python ./bootstrap.py"]