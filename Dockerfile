FROM python:3.12.3-alpine3.20

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN mkdir /app/logs && \
    apk add --no-cache tzdata build-base && \
    pip install --no-cache-dir poetry && \
    pip install "tgcrypto==1.2.5" --no-binary :all: && \
    poetry install --no-root --no-dev

COPY . .

WORKDIR /app/src

CMD ["poetry", "run", "python", "main.py"]