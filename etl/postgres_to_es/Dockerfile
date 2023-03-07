FROM python:3.10.8-bullseye

ENV \
    PYTHONPATH=/usr/local/bin/python3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

COPY ["requirements.txt", "backend_conf.py", "etl_process.py", "extract.py", "transform.py", "load.py", "es_schema.json", "genre_schema.json", "./"]

RUN \
    mkdir app \
    && groupadd -r es && useradd -d /app -r -g es es \
    && mv etl_process.py /app/etl_process.py \
    && mv backend_conf.py /app/backend_conf.py \
    && mv extract.py /app/extract.py \
    && mv transform.py /app/transform.py \
    && mv load.py /app/load.py \
    && mv es_schema.json /app/es_schema.json \
    && mv genre_schema.json /app/genre_schema.json \
    && chown es:es -R /app \
    && python -m pip install --upgrade pip \
    && pip install --upgrade wheel \
    && python3 -m pip install -r requirements.txt

WORKDIR /app

USER es

ENTRYPOINT [ "python", "etl_process.py" ]