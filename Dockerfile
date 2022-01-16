FROM python:3.8-slim

RUN apt-get update \ 
    && apt-get install -y git vim nkf unzip sudo curl

COPY ./requirements.txt /tmp/

RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt
