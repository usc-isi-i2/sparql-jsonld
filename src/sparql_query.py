from rdflib.plugins.sparql.parser import parseQuery


from .temp_for_test import select2construct


class SPARQLQuery(object):
    def __init__(self, query: str, frame: dict = None):
        """
        Init a SPARQLQuery object with SPARQL query string
        :param query: a SPARQL query string
        """
        self._str_query = query
        self._str_need_update = False

        self._parsed_query = self.parse_query(query)
        if frame:
            self.update_query_by_frame(frame)

    @property
    def str_query(self):
        if self._str_need_update:
            self.generate_new_string()
        return self._str_query

    @property
    def parsed_query(self):
        return self._parsed_query

    def update_query_by_frame(self, frame: dict):
        """
        Convert a select query to a construct query based on the info from the frame
        :param frame:
        """

        # TODO: modify the content of the query ...
        self.frame = frame
        pass

        self._str_need_update = True

    def generate_new_string(self):
        """
        convert a structured query back to a string
        """

        # TODO: convert the tree back to string
        new_str = select2construct(self._str_query, self.frame)
        pass

        self._str_query = new_str
        self._str_need_update = False

    @staticmethod
    def parse_query(query: str):
        """
        Parse a string query to structured data
        :param query:
        :return:
        """

        # TODO: parse the query ...
        parsed_query = parseQuery(query) # a pyparsing.ParseResult object

        return parsed_query
