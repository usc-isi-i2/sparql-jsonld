from src.query_wrapper import QueryWrapper
import json

endpoint = "http://dbpedia.org/sparql"
with open('../resources/context.json') as f:
    context = json.load(f)

for i in range(1, 6):
    print('\n----- example %d -----' % i)
    with open('../resources/frame%d.json' % i) as f:
        frame = json.load(f)
    with open('../resources/query%d.txt' % i) as f:
        query = f.read()

    graph = QueryWrapper(endpoint)
    res = graph.query(query, frame, context)

    print(json.dumps(res['@graph'], indent=2))
