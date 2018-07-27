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
    print('\n------ try %s -------' % filename)
    # if filename != 'attack_desc_created_date.txt':
    #     continue
    if filename.replace('.txt', '.json') in frame_files:
        with open('../resources/prod_query/frame/%s' % filename.replace('.txt', '.json')) as frame_f:
            frame = json.load(frame_f)
    else:
        frame = {}

    with open('../resources/prod_query/query/%s' % filename) as query_f:
        query = query_f.read()

    start = time.time()
    res = graph.query(query, frame, context)

    time_query = res.get('time_query', -1)
    time_frame = res.get('time_frame', -1)
    res = res.get('@graph', {})

    print('time query: %f, time frame: %f' % (time_query, time_frame))
    print(len(res))

    log_querytime(filename[:-4], int(time_query), endpoint, full_query=query)

    # print(json.dumps(res, indent=2))
