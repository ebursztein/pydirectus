"""used to collect directus raw responses for testing
don't dump PII data, sensitive data or production data
"""
import json
from rich import print
from pydirectus import Directus
from pathlib import Path
from rich.progress import track

# list of endpoints to dump
END_POINTS = ['collections/books','fields/books',
              'collections/test', 'fields/test',]


def dump_data(endpoint):
    "write directus response to test_data folder"
    dr = Directus()
    data = dr.get_raw_endpoint(endpoint)
    p = Path('pydirectus/test_data') / f'{endpoint}.json'
    if not p.parent.exists():
        p.parent.mkdir(parents=True)
    with open(p, 'w') as f:
        json.dump(data, f, indent=2)


dr = Directus()
dr.ping()

for e in track(END_POINTS, description='Dumping directus raw responses'):
    dump_data(e)
