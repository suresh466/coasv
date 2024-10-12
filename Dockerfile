# syntax=docker/dockerfile:1
FROM python:3.12
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install netcat
RUN apt update && apt install -y netcat-openbsd

WORKDIR /app
COPY . /app/

# ensure entrypoint.sh is executable
RUN chmod +x /app/entrypoint.sh

RUN pip install django-coasc*.tar.gz
RUN pip install -r requirements.txt

