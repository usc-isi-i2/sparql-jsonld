from src.graph_db import GraphDB
from src.sparql_query import SPARQLQuery
from src.framer import Framer


class Wrapper(object):
    def __init__(self):
        pass

    @staticmethod
    def query(query, frame, context, endpoint='http://dbpedia.org/sparql', optional=True):
        graph = GraphDB(endpoint)
        q = SPARQLQuery(query)

        framer = Framer(context)
        q.update_query_by_frame(framer, frame, optional=optional)

        res = graph.query(q)

        return res.nested_jsonld
