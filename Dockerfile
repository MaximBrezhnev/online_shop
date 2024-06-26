FROM python:3.11
RUN apt-get update -y
RUN apt-get upgrade -y

ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . .

RUN mkdir online_shop/static

RUN pip install -r requirements.txt
