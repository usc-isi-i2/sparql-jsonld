from rdflib.term import Variable, Literal, URIRef
from rdflib.plugins.sparql.sparql import CompValue
from pyparsing import ParseResults
from rdflib.plugins.sparql.parserutils import plist


class Updater(object):
    def __init__(self, context: dict=None):
        self.current_naming = 1
        self.context = context if context else {}
        self.prefix = {}
        self.exist_triples = {}

    def update(self, tree: ParseResults, frame: dict, optional: bool=True) -> ParseResults:
        """
        update a tree based on a json frame
        :param tree: the query tree to be updated
        :param frame: the frame in json (expected output format)
        :param optional: if the extra attributes in the frame is optional, default to be true
        :return: return the updated tree in ParseResults
        """

        if '@context' in frame:
            self.context = dict(self.context, **frame['@context'])

        try:
            temp = tree[1]['projection'][0]
            parent = temp['var'] if 'var' in temp else temp['evar']

            self.prefix = self.prefix2dict(tree[0])
            self.exist_triples = self.where2triples(tree[1]['where']['part'])
        except KeyError as ke:
            print('KeyError when parsing existing query: ', ke)
            return ParseResults([])
        except Exception as e:
            print(e)
            return ParseResults([])

        triples = []
        extra = []

        # convert the frame to triples in the same structure with parsed query
        self.frame2triple(frame, parent, triples, extra)

        # generate the ConstructQuery CompValue
        new_query = CompValue(name='ConstructQuery')

        new_template = plist([ParseResults(x) for x in triples])
        new_query['template'] = new_template

        for k, v in tree[-1].items():
            if k not in ['projection', 'modifier']:
                if k == 'where' and 'part' in v:
                    if optional:
                        for x in extra:
                            v['part'].append(
                                CompValue(
                                    'OptionalGraphPattern',
                                    graph=CompValue('TriplesBlock',
                                                    triples=plist([ParseResults(triples[x])]))))
                    else:
                        v['part'].append(CompValue('TriplesBlock',
                                                   triples=plist([ParseResults(triples[x]) for x in extra])))
                new_query[k] = v

        return ParseResults([tree[0], new_query])

    def frame2triple(self, root: dict, parent: Variable, triples: list, extra: list) -> None:
        """
        convert a json frame to s-p-o triples recursively
        :param root: json frame
        :param parent: subject for now
        :param triples: a list to store the results
        :param extra: indeces of extra triples
        """
        for k, v in root.items():
            if k == '@context':
                continue
            p = self.to_node(k)
            if isinstance(v, str):
                o = self.to_node(v)
            else:
                if (parent.toPython(), k) in self.exist_triples:
                    o = Variable(self.exist_triples[(parent.n3(), k)])
                else:
                    o = Variable('var%d' % self.current_naming)
                    self.current_naming += 1
                    extra.append(len(triples))
            if not isinstance(p, Literal):
                triples.append([parent, p, o])
            else:
                print('failed to find context of %s.' % p)
            if isinstance(v, dict) and len(v):
                self.frame2triple(v, o, triples, extra)

    def to_node(self, value: str) -> object:
        if value in self.context and isinstance(self.context[value], dict) and '@id' in self.context[value]:
            full = self.context[value]['@id']
            local_name = full.split('/')[-1]
            pre = full[:-len(local_name)]
            if pre in self.prefix:
               return CompValue(name='pname', prefix=self.prefix[pre], localname=local_name)
            return URIRef(self.context[value]['@id'])
        else:
            if value in self.context and isinstance(self.context[value], str):
                value = self.context[value]
            split = value.split(':')
            if len(split) == 2:
                return CompValue(name='pname', prefix=split[0], localname=split[1])
            if value.startswith('@'):
                return CompValue(name='pname', prefix='rdf', localname=value[1:])
            return Literal(value)

    @staticmethod
    def where2triples(triple_blocks):
        from src.stringify import ele2str
        ret = {}
        for block in triple_blocks:
            if isinstance(block, CompValue) and block.name == 'TriplesBlock' and 'triples' in block:
                for tri in block['triples']:
                    s, p, o = [ele2str(x).split(':')[-1] for x in tri]
                    p = '@'+p if p in ['type', 'id', 'explicit'] else p
                    ret[(s, p)] = o
        return ret


    @staticmethod
    def prefix2dict(tree_prefix):
        try:
            ret = {}
            for pre in tree_prefix:
                if isinstance(pre, CompValue) and pre.name == 'PrefixDecl':
                    ret[pre['iri'].toPython()] = pre['prefix'] if 'prefix' in pre else ''
            return ret
        except Exception as e:
            print(e)
            return {}




