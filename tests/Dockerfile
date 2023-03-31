FROM python:3.10.8-bullseye

ENV \
    PYTHONPATH=/usr/local/bin/python3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

RUN mkdir -p /tests

COPY ./ /tests

RUN \
    # apt update && apt install -y vim \
    # && groupadd -r tester && useradd -d /tests -r -g tester tester \
    # && chown tester:tester -R /tests \
    pip install --upgrade wheel \
    && python3 -m pip install -r tests/functional/requirements.txt



WORKDIR /tests/functional

# USER tester

# ENTRYPOINT pytest src/test_persons.py
CMD [ "tail", "-f", "/dev/null" ]