# syntax=docker/dockerfile:1.4
FROM python:3.10-slim-bookworm

WORKDIR /usr/src/app

# Install build dependencies for MySQL client
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run_app.py"]
