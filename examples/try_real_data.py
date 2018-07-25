from src.query_wrapper import QueryWrapper
import json, os, time

endpoint = "http://kg2018a.isi.edu:3030/test/sparql"
# endpoint = "http://localhost:3030/ds/query"
graph = QueryWrapper(endpoint)

with open('../resources/karma_context.json') as f:
    context = json.load(f)

for filename in os.listdir('../resources/frames'):
    print('\n------ try %s -------' % filename)
    with open('../resources/frames/%s' % filename) as f:
        frame = json.load(f)

    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX scm: <http://schema.org/>
    PREFIX dig: <http://schema.dig.isi.edu/ontology/>
    PREFIX eff: <http://effect.isi.edu/data/>
    
    SELECT ?s
    WHERE {
      ?s rdf:type dig:%s .
    } LIMIT 2
    """ % frame['@type']
    s = time.time()
    res = graph.query(query, frame, context)
    # print(time.time()-s)

    print(json.dumps(res['@graph'], indent=2))
