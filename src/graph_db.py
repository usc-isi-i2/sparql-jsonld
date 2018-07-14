from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.query import Result
from SPARQLWrapper import XML, JSON, JSONLD

from .sparql_query import SPARQLQuery
from .nested_rdf import NestedRDF


class GraphDB(object):
    """
    A Starter is used for initializing a Graph and do the SPARQL queries.
    """

    def __init__(self, database: str):
        """
        Init a starter with address of a database
        :param database: str - query endpoint of the database

        """

        self.graph = Graph(SPARQLStore(endpoint=database, context_aware=False))
        # More possible params:
        # https://github.com/RDFLib/rdflib/blob/d62fa7075da684ffa216c8e6f98cfb3554bb64ab/rdflib/plugins/stores/sparqlstore.py

    def query(self, query: str or SPARQLQuery):
        """
        Take in a SPARQL query and return the final nested results as a list of json objects
        :param query: a SPARQL query string or a QueryUnit object
        :return: RDFWrapper holding the results
        """

        res = self.send_query(query)

        return self.wrap(res)

    def send_query(self, query: str or SPARQLQuery):
        """
        Take in a SPARQL CONSTRUCT query and send it to the database, return a ConjunctiveGraph
        :param query: a SPARQL query string or a QueryUnit object
        :return: query results
        """

        try:
            if isinstance(query, str):
                res = self.graph.query(query)
            elif isinstance(query, SPARQLQuery):
                res = self.graph.query(query.str_query)
            else:
                raise Exception('Invalid Type of "query".')
        except Exception:
            raise Exception('Invalid Query')

        return res

    @staticmethod
    def wrap(res: Result):
        # see https://github.com/RDFLib/rdflib/blob/master/rdflib/query.py
        if res.type == 'CONSTRUCT':
            return NestedRDF(res.serialize(format='json-ld'))
        elif res.type == 'SELECT':
            pass
        elif res.type == 'ASK':
            pass
        elif res.type == 'DESCRIBE':
            pass
        else:
            print('Unknown type.')
        return None

