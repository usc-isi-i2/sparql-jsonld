from src.graph_db import GraphDB
from src.sparql_query import SPARQLQuery
import json

db = "http://dbpedia.org/sparql"

for i in range(1, 4):
    with open('../resources/frame%d.json' % i) as f:
        frame = json.load(f)
    with open('../resources/query%d.txt' % i) as f:
        query = f.read()

    graph = GraphDB(db)
    q = SPARQLQuery(query, frame)
    res = graph.query(q)

    print(json.dumps(res.nested_jsonld, indent=2))