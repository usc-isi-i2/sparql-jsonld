import unittest
from rdflib.plugins.sparql.parser import parseQuery
from src.updater import Updater


class TestUpdater(unittest.TestCase):
    def test_updater(self) -> None:
        ori = parseQuery("""PREFIX  dc:  <http://purl.org/dc/elements/1.1/>
PREFIX  ns:  <http://example.org/ns#>
SELECT  ?title (?p*(1-?discount) AS ?price)
{ ?x ns:price ?p .
  ?x dc:title ?title .
  ?x ns:discount ?discount
}""")
        frame = {
            '@context': {
                'price': {
                    '@id': 'http://example.org/ns#price'
                },
                'title': {
                    '@id': 'http://purl.org/dc/elements/1.1/title'
                }
            },
            'price': {},
            'title': {}
        }
        u = Updater()
        res = u.update(ori, frame).dump().split('\n')[0].replace('\n', '')

        expect = """[[PrefixDecl_{'prefix': 'dc', 'iri': rdflib.term.URIRef('http://purl.org/dc/elements/1.1/')}, \
PrefixDecl_{'prefix': 'ns', 'iri': rdflib.term.URIRef('http://example.org/ns#')}], ConstructQuery_{'template': \
[([rdflib.term.Variable('title'), rdflib.term.URIRef('http://example.org/ns#price'), rdflib.term.Variable\
('var1')], {}), ([rdflib.term.Variable('title'), pname_{'prefix': 'dc', 'localname': 'title'}, rdflib.term.\
Variable('var2')], {})], 'where': GroupGraphPatternSub_{'part': [TriplesBlock_{'triples': [([rdflib.term.\
Variable('x'), PathAlternative_{'part': [PathSequence_{'part': [PathElt_{'part': pname_{'prefix': 'ns', \
'localname': 'price'}}]}]}, rdflib.term.Variable('p')], {}), ([rdflib.term.Variable('x'), PathAlternative_\
{'part': [PathSequence_{'part': [PathElt_{'part': pname_{'prefix': 'dc', 'localname': 'title'}}]}]}, rdflib.\
term.Variable('title')], {}), ([rdflib.term.Variable('x'), PathAlternative_{'part': [PathSequence_{'part': \
[PathElt_{'part': pname_{'prefix': 'ns', 'localname': 'discount'}}]}]}, rdflib.term.Variable('discount')], \
{})]}, OptionalGraphPattern_{'graph': TriplesBlock_{'triples': [([rdflib.term.Variable('title'), rdflib.term.\
URIRef('http://example.org/ns#price'), rdflib.term.Variable('var1')], {})]}}, OptionalGraphPattern_{'graph': \
TriplesBlock_{'triples': [([rdflib.term.Variable('title'), pname_{'prefix': 'dc', 'localname': 'title'}, \
rdflib.term.Variable('var2')], {})]}}]}}]"""

        self.assertEqual(res.strip(), expect)

    def test_updater_no_frame(self) -> None:
        ori = parseQuery("""PREFIX  dc:  <http://purl.org/dc/elements/1.1/>
        PREFIX  ns:  <http://example.org/ns#>
        SELECT  ?title (?p*(1-?discount) AS ?price)
        { ?x ns:price ?p .
          ?x dc:title ?title .
          ?x ns:discount ?discount
        }""")

        u = Updater()
        res = u.update(ori, {}).dump().split('\n')[0].replace('\n', '')

        expect = """[[PrefixDecl_{'prefix': 'dc', 'iri': rdflib.term.URIRef('http://purl.org/dc/elements/1.1/')}, \
PrefixDecl_{'prefix': 'ns', 'iri': rdflib.term.URIRef('http://example.org/ns#')}], ConstructQuery_{'template': \
[], 'where': GroupGraphPatternSub_{'part': [TriplesBlock_{'triples': [([rdflib.term.Variable('x'), \
PathAlternative_{'part': [PathSequence_{'part': [PathElt_{'part': pname_{'prefix': 'ns', 'localname': 'price'\
}}]}]}, rdflib.term.Variable('p')], {}), ([rdflib.term.Variable('x'), PathAlternative_{'part': [PathSequence_\
{'part': [PathElt_{'part': pname_{'prefix': 'dc', 'localname': 'title'}}]}]}, rdflib.term.Variable('title')], \
{}), ([rdflib.term.Variable('x'), PathAlternative_{'part': [PathSequence_{'part': [PathElt_{'part': pname_{\
'prefix': 'ns', 'localname': 'discount'}}]}]}, rdflib.term.Variable('discount')], {})]}]}}]"""

        self.assertEqual(res, expect)
