FROM python:3.12-alpine

WORKDIR /app
COPY shipbot/ /app/shipbot/

ENTRYPOINT ["python", "/app/shipbot/main.py"]