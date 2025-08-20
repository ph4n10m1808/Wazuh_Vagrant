# query_opensearch.py

from datetime import datetime, timedelta
from opensearchpy import OpenSearch, RequestsHttpConnection
from config import OPENSEARCH_CONFIG

def connect_opensearch():
    return OpenSearch(
        hosts=[{'host': OPENSEARCH_CONFIG['host'], 'port': OPENSEARCH_CONFIG['port']}],
        http_auth=(OPENSEARCH_CONFIG['user'], OPENSEARCH_CONFIG['password']),
        use_ssl=OPENSEARCH_CONFIG['use_ssl'],
        verify_certs=OPENSEARCH_CONFIG['verify_certs'],
        connection_class=RequestsHttpConnection
    )

def query_recent_logs(last_ts=None):
    client = connect_opensearch()

    all_logs = []
    # page_size = 500
    search_after = None

    query_time_range = {
        "range": {
            "@timestamp": {
                "gte": last_ts if last_ts else "now-30s"
            }
        }
    }

    while True:
        query = {
            # "size": page_size,
            "sort": [{"@timestamp": "asc"}],
            "query": query_time_range
        }

        if search_after:
            query["search_after"] = search_after

        res = client.search(index=OPENSEARCH_CONFIG['index'], body=query)
        hits = res['hits']['hits']

        if not hits:
            break

        all_logs.extend([hit['_source'] for hit in hits])
        search_after = hits[-1]['sort']

    return all_logs
