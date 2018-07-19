from rdflib.plugins.sparql.parser import parseQuery


from .framer import Framer
from .stringify import stringify


class SPARQLQuery(object):
    def __init__(self, query: str):
        """
        Init a SPARQLQuery object with SPARQL query string
        :param query: a SPARQL query string
        """
        self._str_query = query
        self._str_need_update = False

        self.parsed_query = parseQuery(query)

    @property
    def str_query(self):
        if self._str_need_update:
            self.generate_new_string()
        return self._str_query

    def update_query_by_frame(self, framer: Framer, frame: dict):
        """
        Convert a select query to a construct query based on the info from the frame
        """
        self.parsed_query = framer.frame(self.parsed_query, frame)
        self._str_need_update = True

    def generate_new_string(self):
        """
        convert a structured query back to a string
        """
        new_str = stringify(self.parsed_query)

        self._str_query = new_str
        self._str_need_update = False

