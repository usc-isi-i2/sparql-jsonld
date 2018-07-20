import unittest
from src.query_wrapper import QueryWrapper

qw = QueryWrapper('http://dbpedia.org/sparql')
query_str = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT (SAMPLE(?name) AS ?name_of_university)
WHERE {
  ?univ foaf:name ?name .
  ?univ rdf:type dbo:University .
  ?univ dbo:state dbr:Oregon .
  FILTER regex(?name, "of")
} ORDER BY ?name LIMIT 10
"""


class TestQuery(unittest.TestCase):

    def test_query_str(self) -> None:
        try:
            qw.query(query_str)
            good = True
        except Exception:
            good = False

        self.assertEqual(good, True)
