FROM python:3.10.5-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

VOLUME /sentdebot
WORKDIR /sentdebot

RUN /usr/local/bin/python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --user
COPY . .

ENTRYPOINT [ "python3", "sentdebot.py" ]
