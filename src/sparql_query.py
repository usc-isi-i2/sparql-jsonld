from rdflib.plugins.sparql.parser import parseQuery


from .framer import Framer
from .tree_stringifier import TreeStringifier


class SPARQLQuery(object):
    def __init__(self, query: str, frame: dict = None):
        """
        Init a SPARQLQuery object with SPARQL query string
        :param query: a SPARQL query string
        """
        self._str_query = query
        self._str_need_update = False

        self.framer = Framer()
        self.stringify = TreeStringifier()

        self.parsed_query = parseQuery(query)
        if frame:
            self.update_query_by_frame(frame)

    @property
    def str_query(self):
        if self._str_need_update:
            self.generate_new_string()
        return self._str_query

    def update_query_by_frame(self, frame: dict):
        """
        Convert a select query to a construct query based on the info from the frame
        :param frame:
        """
        self.parsed_query = self.framer.frame(self.parsed_query, frame)
        self._str_need_update = True

    def generate_new_string(self):
        """
        convert a structured query back to a string
        """
        new_str = self.stringify.format(self.parsed_query)

        self._str_query = new_str
        self._str_need_update = False

