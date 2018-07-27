import unittest
from rdflib.plugins.sparql.parser import parseQuery
from src.stringify import stringify


class TestStringify(unittest.TestCase):
    def test_stringify_select(self) -> None:
        tree = parseQuery("""
        PREFIX : <http://people.example/>
        SELECT ?y ?minName
        WHERE {
          :alice :knows ?y .
          {
            SELECT ?y (MIN(?name) AS ?minName)
            WHERE {
              ?y :name ?name .
            } GROUP BY ?y
          }
        }
        """)
        res = stringify(tree)
        expect = """PREFIX : <http://people.example/>
SELECT ?y ?minName 
WHERE { 
:alice :knows ?y .
{
SELECT ?y (MIN(?name) AS ?minName) 
WHERE { 
?y :name ?name .

}
 GROUP BY ?y 

}
}"""
        self.assertEqual(res.strip(), expect)

    def test_stringify_construct(self) -> None:
        tree = parseQuery("""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX : <http://dbpedia.org/resource/>
CONSTRUCT { ?person foaf:name ?name . }
WHERE {
      ?person a dbo:MusicalArtist .
      ?person dbo:birthPlace :Berlin .
      ?person foaf:name ?name .
      FILTER (LANG(?description) = 'en') . 
} ORDER BY ?name
                """)
        res = stringify(tree)
        expect = """PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX : <http://dbpedia.org/resource/>
CONSTRUCT {?person foaf:name ?name .} 
WHERE { 
?person <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> dbo:MusicalArtist .
?person dbo:birthPlace :Berlin .
?person foaf:name ?name .

FILTER ( LANG(?description) = "en" ) .

}
 ORDER BY ?name"""
        self.assertEqual(res.strip(), expect)
