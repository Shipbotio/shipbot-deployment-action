FROM python:3.12.8-alpine3.21

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "/app/main.py"]
