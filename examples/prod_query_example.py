from src.query_wrapper import QueryWrapper
from log.querytime import log_querytime
import json, os, time

# endpoint = "http://kg2018a.isi.edu:3030/test/sparql"
# endpoint = "http://localhost:3030/ds/query"
endpoint = "http://kg2018a.isi.edu:3030/fixed/sparql"
graph = QueryWrapper(endpoint)

with open('../resources/karma_context.json') as f:
    context = json.load(f)

frame_files = set(os.listdir('../resources/prod_query/frame'))

for filename in os.listdir('../resources/prod_query/query'):
    # if filename != 'three_entity_date_aggs.txt':
    #     continue
    print('\n------ try %s -------' % filename)
    if filename.replace('.txt', '.json') in frame_files:
        with open('../resources/prod_query/frame/%s' % filename.replace('.txt', '.json')) as frame_f:
            frame = json.load(frame_f)
    else:
        frame = {}

    with open('../resources/prod_query/query/%s' % filename) as query_f:
        query = query_f.read()

    res = graph.query(query, frame, context)

    lr, lb, tq, tf = res.get('@info', {1: -1, 2: -1, 3: -1, 4:-1}).values()
    print(lr, lb, tq, tf)
    log_querytime(filename[:-4], lr, lb, tq, tf, endpoint, full_query=query)

    with open('./outputs/%s' % filename, 'w') as f:
        json.dump(res.get('@graph', {}), f, indent=2)
