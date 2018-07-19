from src.graph_db import GraphDB
from src.sparql_query import SPARQLQuery
from src.framer import Framer
import json

db = "http://dbpedia.org/sparql"
with open('../resources/context.json') as f:
    context = json.load(f)
if '@context' in context:
    context = context['@context']

for i in range(1, 5):
    print('\n----- example %d -----' % i)
    with open('../resources/frame%d.json' % i) as f:
        frame = json.load(f)
    with open('../resources/query%d.txt' % i) as f:
        query = f.read()

    graph = GraphDB(db)
    q = SPARQLQuery(query)

    framer = Framer(context)
    q.update_query_by_frame(framer, frame)

    # print(q.str_query)

    res = graph.query(q)

    print(json.dumps(res.nested_jsonld, indent=2))
