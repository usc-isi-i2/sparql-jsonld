from src.tree_stringifier import TreeStringifier
from rdflib.plugins.sparql.parser import parseQuery

from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore

# https://github.com/RDFLib/rdflib/pull/744/commits/654bc787a5449f7e331860a67cb993226ac99585

from SPARQLWrapper import SPARQLWrapper, JSON


db = 'http://dbpedia.org/sparql'

tf = TreeStringifier()
g = Graph(SPARQLStore(endpoint=db, context_aware=False))
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

for i in range(1, 18, 1):
    print('\n\n ========%d==========' % (i))
    with open('example_queries/%d.txt' % (i)) as f:
        q = f.read()

    try:
        expected = g.query(q)
        print(' -  Can Query')
    except Exception as e:
        try:
            sparql.setQuery(q)
            res = sparql.query()
            print(' -  Can Query')
        except Exception as e_:
            print(' x Fail Query', e, e_)
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
    except Exception as e:
        try:
            sparql.setQuery(q_)
            res = sparql.query()
            print(' -  Good Revert')
        except Exception as e_:
            print(q)
            print()
            print(q_)
            print(' x Fail Query', e, e_)
            continue
