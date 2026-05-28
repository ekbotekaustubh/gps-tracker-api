# syntax=docker/dockerfile:1.4
FROM python:3.10-slim-bookworm

WORKDIR /usr/src/app

# Combine apt-get commands to keep the image slim and prevent cache issues
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Your monkey-patch for older Flask extensions running on Flask 2.x+
RUN sed -i '/_request_ctx_stack/d' /usr/local/lib/python3.10/site-packages/flask/__init__.py 

EXPOSE 5000

CMD ["python", "manage.py", "runserver"]
