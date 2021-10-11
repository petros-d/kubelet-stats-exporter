FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY exporter.py .

ENTRYPOINT ["python", "-u", "/app/exporter.py"]