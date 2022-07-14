FROM python:3.9
ENV PYTHONUNBUFFERED=1
RUN mkdir /backend
WORKDIR /backend

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get install -yq netcat curl

COPY . /backend