import time
import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

if __name__ == '__main__':
    es_client = Elasticsearch(
        hosts=os.environ.get('ELASTIC_HOST'),
        validate_cert=False,
        use_ssl=False,
    )
    while True:
        if es_client.ping():
            break
        time.sleep(1)
