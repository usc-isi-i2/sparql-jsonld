from rdflib.plugins.sparql.parser import parseQuery


from .updater import Updater
from .stringify import stringify


class SPARQLQuery(object):
    def __init__(self, query: str) -> None:
        """
        Init a SPARQLQuery object with SPARQL query string
        :param query: a SPARQL query string
        """
        self._str_query = query
        self._str_need_update = False

        self.parsed_query = parseQuery(query)

    @property
    def str_query(self) -> str:
        if self._str_need_update:
            self.generate_new_string()
        return self._str_query

    def update_query_by_frame(self, updater: Updater, frame: dict, optional: bool=True) -> None:
        """
        Convert a select query to a construct query based on the info from the frame
        """
        self.parsed_query = updater.update(self.parsed_query, frame, optional=optional)
        self._str_need_update = True

    def generate_new_string(self) -> None:
        """
        convert a structured query back to a string
        """
        new_str = stringify(self.parsed_query)

        self._str_query = new_str
        self._str_need_update = False

