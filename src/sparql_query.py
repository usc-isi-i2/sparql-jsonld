from rdflib.plugins.sparql.parser import parseQuery
from SPARQLWrapper import SPARQLWrapper, JSON

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

        self.init_query = query
        self.parsed_query = parseQuery(query)

        self.has_limit = 'limit' in query.split('}')[-1].lower()

    @property
    def str_query(self) -> str:
        if self._str_need_update:
            self.generate_new_string()
        return self._str_query

    def update_query_by_frame(self, updater: Updater, frame: dict, optional: bool=True, specified_subjects: list=None) -> None:
        """
        Convert a select query to a construct query based on the info from the frame
        """
        self.parsed_query = updater.update(self.parsed_query, frame, optional=optional, specified_subjects=specified_subjects)
        self._str_need_update = True

    def generate_new_string(self) -> None:
        """
        convert a structured query back to a string
        """
        new_str = stringify(self.parsed_query)

        self._str_query = new_str
        self._str_need_update = False

    def get_limit_subjects(self, graph: SPARQLWrapper):
        if self.has_limit:
            ret = []
            # TODO: DISTINCT ??
            graph.setQuery(self.init_query)
            graph.setReturnFormat(JSON)
            res = graph.query().convert()['results']['bindings']
            for r in res:
                for v in r.values():
                    if 'value' in v and v.get('type') == 'uri':
                        ret.append(v['value'])
            return ret
        return []

