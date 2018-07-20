from SPARQLWrapper import SPARQLWrapper, JSONLD, JSON
from pyld import jsonld
import json

from .sparql_query import SPARQLQuery
from .updater import Updater



class QueryWrapper(object):
    """
    A Starter is used for initializing an endpoint to graph and do the SPARQL queries.
    """

    def __init__(self, database: str) -> None:
        """
        Init a starter with address of a database
        :param database: str - query endpoint of the database

        """

        self.graph = SPARQLWrapper(database)

    def query(self, query: str, frame: dict=None, context: dict=None, optional: bool=True) -> dict:
        """
        Take in a SPARQL query and return the final nested results as a list of json objects
        :param query: a SPARQL query string
        :param frame: a json frame
        :param context: context for the frame in json
        :param optional: if the extra fields in the frame is optional, default to be true(optional)
        :return: a dict holding nested json-ld results
        """

        if frame:
            if '@context' in context:
                context = context['@context']
            # parse and update the query by the frame:
            q = SPARQLQuery(query)
            updater = Updater(context)
            q.update_query_by_frame(updater, frame, optional=optional)

            # query with the updated query:
            self.graph.setQuery(q.str_query)
            self.graph.setReturnFormat(JSONLD)
            res = self.graph.query().convert().serialize(format='json-ld')
            frame_with_context = {
                '@context': updater.context,
                **frame
            }

            framed = jsonld.frame(json.loads(res.decode('utf-8')), frame_with_context)
            return framed

        # no frame, just send the original query to the endpoint:
        else:
            self.graph.setQuery(query)
            self.graph.setReturnFormat(JSON)
            res = self.graph.query().convert()
            return res


