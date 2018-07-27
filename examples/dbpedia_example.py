from src.query_wrapper import QueryWrapper
import json

endpoint = "http://dbpedia.org/sparql"
with open('../resources/dbpedia_example/context.json') as f:
    context = json.load(f)

for i in range(1, 6):
    print('\n----- example %d -----' % i)
    with open('../resources/dbpedia_example/frame%d.json' % i) as f:
        frame = json.load(f)
    with open('../resources/dbpedia_example/query%d.txt' % i) as f:
        query = f.read()

    graph = QueryWrapper(endpoint)
    res = graph.query(query, frame, context).get('@graph', {})

    print(json.dumps(res, indent=2))
