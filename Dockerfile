FROM python:3.11
RUN apt-get update -y
RUN apt-get upgrade -y

WORKDIR /app
COPY . .


RUN pip install -r requirements.txt


CMD ["python3", "./online_shop/manage.py", "runserver", "0.0.0.0:7000"]

