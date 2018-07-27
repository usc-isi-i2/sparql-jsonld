from flask import Flask, render_template, request, redirect
from src.query_wrapper import QueryWrapper
import json, os

app = Flask(__name__, template_folder='./')

query_result = '/ * Framed query results * /'
query_str = ''
frame = ''
context = ''
endpoint = ''

query_files = os.listdir('../resources/prod_query/query')
options = ['<option value="%s">%s</option>' % (fname.split('.')[0], fname.split('.')[0]) for fname in query_files]
option_elements = '\n'.join(options)

frame_files = set(os.listdir('../resources/prod_query/frame'))

@app.route('/')
def hello_world():
    global query_str, frame, context, option_elements

    return render_template("index.html",
                           query_result=query_result,
                           endpoint=endpoint,
                           query_str=query_str,
                           frame=frame,
                           context=context,
                           option_elements=option_elements
                           )


@app.route('/query', methods=['POST'])
def query():
    try:
        global query_result
        ep = request.form['endpoint']
        q = request.form['query']
        f = json.loads(request.form['frame'])
        c = json.loads(request.form['context'])

        graph = QueryWrapper(ep)
        res = graph.query(q, f, c)
        query_result = json.dumps(res.get('@graph', {}), indent=2)

        return redirect('/')
    except Exception as e:
        query_result = 'Failed, please check your inputs and try again. \n %s' % str(e)
        return redirect('/')


@app.route('/example/dbpedia', methods=['POST'])
def example_dbpedia():
    global query_str, frame, context, endpoint
    no = request.form['dbpedia']

    with open('../resources/dbpedia_example/query%s.txt' % no) as f:
        query_str = f.read()
    with open('../resources/dbpedia_example/frame%s.json' % no) as f:
        frame = f.read()
    with open('../resources/dbpedia_example/context.json') as f:
        context = f.read()
    endpoint = 'http://dbpedia.org/sparql'

    return redirect('/')


@app.route('/example/realdata', methods=['POST'])
def example_raeldata():
    global query_str, frame, context, endpoint, frame_files

    filename = request.form['realdata']
    with open('../resources/prod_query/query/%s.txt' % filename) as f:
        query_str = f.read()
    if '%s.json' % filename in frame_files:
        with open('../resources/prod_query/frame/%s.json' % filename) as f:
            frame = f.read()
    else:
        frame = {}
    with open('../resources/karma_context.json') as f:
        context = f.read()

    # endpoint = "http://kg2018a.isi.edu:3030/test/sparql"
    # endpoint = "http://localhost:3030/ds/query"
    endpoint = "http://kg2018a.isi.edu:3030/whole/sparql"

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)