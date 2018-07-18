from rdflib.term import Variable, Literal
from rdflib.plugins.sparql.sparql import CompValue
from pyparsing import ParseResults
from rdflib.plugins.sparql.parserutils import plist
import json


class Framer(object):
    def __init__(self):
        self.current_naming = 1
        pass

    def frame(self, tree, frame):
        parent = Variable('main')
        triples = []

        # convert the frame to triples in the same structure with parsed query
        self.frame2triple(frame, parent, triples)

        # generate the ConstructQuery CompValue
        new_query = CompValue(name='ConstructQuery')

        new_template = plist([ParseResults(x) for x in triples])
        new_query['template'] = new_template

        for k, v in tree[-1].items():
            if k not in ['projection', 'modifier']:
                if k == 'where' and 'part' in v:
                    # TODO: deduplicate and make the extra triples optional
                    v['part'].append(CompValue('TriplesBlock', triples=plist([ParseResults(x) for x in triples])))
                new_query[k] = v

        return ParseResults([tree[0], new_query])

    def frame2triple(self, root, parent, triples):
        for k, v in root.items():
            if not k.startswith('@') or isinstance(v, str):
                p, o = self.to_node(k), self.to_node(v, k.split(':')[-1])
                triples.append([parent, p, o])
                if isinstance(v, dict) and len(v):
                    self.frame2triple(v, o, triples)

    def to_node(self, value, name=''):
        # TODO: update the rules here based on how frame json created
        if isinstance(value, str):
            split = value.split(':')
            if len(split) == 2:
                return CompValue(name='pname', prefix=split[0], localname=split[1])
            if value.startswith('@'):
                return CompValue(name='pname', prefix='rdf', localname=value[1:])
            return Literal(value)
        if isinstance(value, dict):
            if not name:
                new_name = 'var%d' % self.current_naming
                self.current_naming += 1
                return Variable(new_name)
            return Variable(name)
        return value



