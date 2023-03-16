FROM python:3.10.8-bullseye

ENV \
    PYTHONPATH=/usr/local/bin/python3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

COPY ["db.sqlite", "load_data.py", "config.py", "requirements.txt", "./"]

RUN \
    mkdir app \
    && groupadd -r loader && useradd -d /app -r -g loader loader \
    && mv load_data.py /app/load_data.py \
    && mv config.py /app/config.py \
    && mv db.sqlite /app/db.sqlite \
    && chown loader:loader -R /app \
    && python -m pip install --upgrade pip \
    && pip install --upgrade wheel \
    && python3 -m pip install -r requirements.txt

WORKDIR /app

USER loader

ENTRYPOINT [ "python", "load_data.py" ]