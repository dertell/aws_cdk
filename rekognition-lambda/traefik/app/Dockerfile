FROM --platform=amd64 python:latest

RUN pip install --upgrade pip

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

COPY . /app

COPY /entrypoint.sh /app

RUN pip install -r requirements.txt

EXPOSE 5000

VOLUME [ "/app" ]

ENTRYPOINT [ "sh", "entrypoint.sh" ]
