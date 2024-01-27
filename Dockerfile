FROM python:alpine

WORKDIR /usr/src/app

ENV DRIVER=playwright-chrome:3000

RUN apk add --no-cache bash

RUN pip install --upgrade pip
COPY . .
RUN pip install -r requirements.txt
RUN chmod +x wait-for-it.sh

CMD ./wait-for-it.sh ${DRIVER}:3000 -- python app.py