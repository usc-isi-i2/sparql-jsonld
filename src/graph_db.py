from SPARQLWrapper import SPARQLWrapper, JSONLD

from .sparql_query import SPARQLQuery
from .nested_rdf import NestedRDF


class GraphDB(object):
    """
    A Starter is used for initializing an endpoint to graph and do the SPARQL queries.
    """

    def __init__(self, database: str) -> None:
        """
        Init a starter with address of a database
        :param database: str - query endpoint of the database

        """

        self.graph = SPARQLWrapper(database)
        self.graph.setReturnFormat(JSONLD)

    def query(self, query: str or SPARQLQuery) -> NestedRDF:
        """
        Take in a SPARQL query and return the final nested results as a list of json objects
        :param query: a SPARQL query string
        :return: a NestedRDF holding nested json results
        """

        if isinstance(query, str):
            self.graph.setQuery(query)
        elif isinstance(query, SPARQLQuery):
            self.graph.setQuery(query.str_query)
        else:
            raise Exception('Invalid Type of "query".')
        res = self.graph.query().convert()

        res = res.serialize(format='json-ld')

        return NestedRDF(res)


