import requests
import json
import urllib3
from config import WAZUH_INDEXER

if not WAZUH_INDEXER["verify_ssl"]:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_alerts(from_timestamp=None):
    url = f"{WAZUH_INDEXER['host']}:{WAZUH_INDEXER['port']}/{WAZUH_INDEXER['index']}/_search"

    headers = {"Content-Type": "application/json"}
    auth = (WAZUH_INDEXER["user"], WAZUH_INDEXER["password"])

    query = {
        "size": 100,
        "sort": [{"@timestamp": "asc"}],
        "query": {
            "range": {
                "@timestamp": {
                    "gt": from_timestamp if from_timestamp else "now-1h"
                }
            }
        }
    }

    response = requests.post(url, headers=headers, auth=auth,
                             data=json.dumps(query),
                             verify=WAZUH_INDEXER["verify_ssl"])
    response.raise_for_status()

    hits = response.json()["hits"]["hits"]
    return [hit["_source"] for hit in hits]
