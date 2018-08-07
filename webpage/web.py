import json, os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from flask import Flask, render_template, request, redirect
from src.query_wrapper import QueryWrapper

app = Flask(__name__, template_folder='./')


def generate_options(filelist):
    options = ['<option value="%s">%s</option>' % (fname.split('.')[0], fname.split('.')[0]) for fname in filelist]
    return '\n'.join(options)

# PROD_ENDPOINT = "http://localhost:3030/ds/query"
PROD_ENDPOINT = "http://gaiadev01.isi.edu:3030/effect/sparql"
DBPEDIA_ENDPOINT = 'http://dbpedia.org/sparql'

with open('../resources/dbpedia_example/context.json') as f:
    DBPEDIA_CONTEXT = f.read()
with open('../resources/karma_context.json') as f:
    PROD_CONTEXT = f.read()
with open('../examples/info.log') as f:
    loginfo = f.readlines()[-len(os.listdir('../resources/prod_query/query')):]
    head = ['QueryName', '#Results', '#Buckets', 'QueryTime/s', 'FramingTime/s', 'TotalTime/s']
    results = ['<tr><th>%s</th></tr>' % '</th><th>'.join(head)]
    for line in loginfo:
        cells = []
        start = 0
        total = 0
        for l in [35, 8, 8, 8, 8]:
            if (start == 51 or start == 59) and int(line[start: start + l].strip()) != -1:
                total += int(line[start: start + l].strip())
            cells.append('<td>%s</td>' % line[start: start + l])
            start += l
        cells.append('<td>%d</td>' % total)
        results.append('<tr>%s</tr>' % ''.join(cells))
    report = '\n'.join(results)
PREFIX = {
    'default': """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX scm: <http://schema.org/>
PREFIX dig: <http://schema.dig.isi.edu/ontology/>
PREFIX eff: <http://effect.isi.edu/data/>
"""}

query_result = '/ * Framed query results * /'
query_str = ''
frame = ''
context = ''
endpoint = ''

option_real_queries = generate_options(os.listdir('../resources/prod_query/query'))
option_full_frames = generate_options(os.listdir('../resources/frames'))
option_prefix = generate_options(list(PREFIX.keys()))

frame_files = set(os.listdir('../resources/prod_query/frame'))


@app.route('/')
def hello_world():
    global query_str, frame, context, option_real_queries, option_full_frames

    return render_template("index.html",
                           query_result=query_result,
                           endpoint=endpoint,
                           query_str=query_str,
                           frame=frame,
                           context=context,
                           option_real_queries=option_real_queries,
                           option_full_frames=option_full_frames,
                           option_prefix=option_prefix,
                           report=report
                           )


@app.route('/query', methods=['POST'])
def query():
    global query_str, frame, context, endpoint, query_result
    try:
        ep = request.form['endpoint']
        query_str = request.form['query']
        frame = request.form['frame']
        context = request.form['context']

        graph = QueryWrapper(ep)
        res = graph.query(query_str, json.loads(frame), json.loads(context))
        query_result = json.dumps(res.get('@graph', {}), indent=2)

        return redirect('/')
    except Exception as e:
        query_result = 'Failed, please check your inputs and try again. \n %s' % str(e)
        return redirect('/')


@app.route('/example/dbpedia', methods=['POST'])
def example_dbpedia():
    global query_str, frame, context, endpoint, query_result
    no = request.form['dbpedia']

    with open('../resources/dbpedia_example/query%s.txt' % no) as f:
        query_str = f.read()
    with open('../resources/dbpedia_example/frame%s.json' % no) as f:
        frame = f.read()
    context = DBPEDIA_CONTEXT
    endpoint = DBPEDIA_ENDPOINT
    query_result = ''

    return redirect('/')


@app.route('/example/realdata', methods=['POST'])
def example_realdata():
    global query_str, frame, context, endpoint, frame_files, query_result

    filename = request.form['realdata']
    with open('../resources/prod_query/query/%s.txt' % filename) as f:
        query_str = f.read()
    if '%s.json' % filename in frame_files:
        with open('../resources/prod_query/frame/%s.json' % filename) as f:
            frame = f.read()
    else:
        frame = {}

    context = PROD_CONTEXT
    endpoint = PROD_ENDPOINT
    query_result = ''

    return redirect('/')


@app.route('/full_frames', methods=['POST'])
def full_frames():
    global frame, context, endpoint, query_result

    filename = request.form['full_frames']

    with open('../resources/frames/%s.json' % filename) as f:
        frame = f.read()

    context = PROD_CONTEXT
    endpoint = PROD_ENDPOINT
    query_result = ''

    return redirect('/')


@app.route('/prefix', methods=['POST'])
def prefix():
    global query_str, context, endpoint, query_result
    filename = request.form['prefix']

    query_str = '%s SELECT ?s WHERE { ?s ?p ?o } \nLIMIT 10' % PREFIX[filename]
    context = PROD_CONTEXT
    endpoint = PROD_ENDPOINT
    query_result = ''

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, port=5002, host='0.0.0.0')
