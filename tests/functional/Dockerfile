FROM python:3.10.8-bullseye

ENV \
    PYTHONPATH=/usr/local/bin/python3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

RUN mkdir -p /functional

COPY ./ /functional

RUN \
    groupadd -r tester && useradd -d /functional -r -g tester tester \
    && chown tester:tester -R /functional \
    && pip install --upgrade wheel \
    && python3 -m pip install -r /functional/requirements.txt



WORKDIR /functional

USER tester

ENTRYPOINT pytest src/