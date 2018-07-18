from src.tree_formatter import TreeFormatter
from rdflib.plugins.sparql.parserutils import prettify_parsetree
from rdflib.plugins.sparql.parser import parseQuery

from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore

db = 'http://dbpedia.org/sparql'
# q = """
# PREFIX foaf: <http://xmlns.com/foaf/0.1/>
# PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# PREFIX dbo: <http://dbpedia.org/ontology/>
# PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# PREFIX dbp: <http://dbpedia.org/property/>
# PREFIX dbr: <http://dbpedia.org/resource/>
# CONSTRUCT {
#   ?univ rdf:type dbo:University .
# }
# WHERE {
#   ?univ rdf:type dbo:University .
#   ?univ dbo:campus dbr:Urban_area .
#   ?univ foaf:name ?name .
#   ?univ dbo:facultySize ?faculty .
#   FILTER (?faculty > 4000) .
# } ORDER BY ?name LIMIT 20
# """


tf = TreeFormatter()
g = Graph(SPARQLStore(endpoint=db, context_aware=False))

for i in range(1, 17, 1):
    print('\n\n ========%d========== \n' % (i))
    with open('example_queries/%d.txt' % (i)) as f:
        q = f.read()

    try:
        expected = g.query(q)
        print(' -  Can Query')
    except Exception as e:
        print(' x Fail Query', e)
        continue

    try:
        parsed = parseQuery(q)
        print(' -  Can Parse')
    except Exception as e:
        print(' x Fail Parse', e)
        continue

    try:
        q_ = tf.format(parsed)
        print(' -  Can Revert')
    except Exception as e:
        print(' x Fail Revert', e)
        continue

    try:
        test = g.query(q_)
        print(' -  Good Revert')
        print(expected.serialize())
        print(test.serialize())
    except Exception as e:
        print(' x Bad Revert', e)
        print(q_)
        # print(prettify_parsetree(parsed))
        continue