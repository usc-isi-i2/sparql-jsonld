from rdflib.plugins.sparql.parserutils import prettify_parsetree, CompValue
from rdflib.term import URIRef, Literal, BNode, Variable
from pyparsing import ParseResults

# TODO: refactor, support [], functions, graph etc.

class TreeStringifier(object):
    def __init__(self):
        self.fixed_recursion = {
            'where': '\nWHERE { \n%s\n}\n',
            'orderby': 'ORDER BY %s\n',
            'groupby': 'GROUP BY %s\n',
            'datasetClause': 'FROM %s'
        }

    def format(self, query_tree):
        if isinstance(query_tree, ParseResults):
            return self.tree2str(query_tree)

    def ele2str(self, ele):
        if isinstance(ele, Literal):
            return str(ele.value)
        elif isinstance(ele, BNode):
            ret = str(ele.toPython())
            return ret if ret[0] == '_' else '[]'
        elif isinstance(ele, (URIRef, Variable)):
            return ele.n3()
        elif isinstance(ele, CompValue):
            if ele.name == 'pname' and 'localname' in ele:
                pref = ele['prefix'] if 'prefix' in ele else ''
                return '%s:%s' % (pref, ele['localname'])
            elif ele.name.startswith('Path') and len(ele) == 1 and 'part' in ele:
                return self.ele2str(ele['part'])
            elif ele.name.endswith('Expression'):
                if len(ele) == 1 and 'expr' in ele:
                    return self.ele2str(ele['expr'])
                elif ele.name == 'ConditionalAndExpression':
                    return self.list2str(list(ele.values()), self.ele2str, joiner=' && ')
                elif ele.name == 'AdditiveExpression':
                    return '(%s)' % self.list2str(list(ele.values()), self.ele2str, joiner=' ')
                else:
                    return self.list2str(list(ele.values()), self.ele2str, joiner=' ')
            elif ele.name == 'UnaryNot' and 'expr' in ele:
                return '!%s' % (self.ele2str(ele['expr']))
            elif ele.name.startswith('Aggregate_'):
                return '%s(%s)' % (ele.name[10:].upper(), self.ele2str(ele['vars']))
            elif ele.name == 'vars':
                if 'var' in ele:
                    return self.ele2str(ele['var'])
                elif 'expr' and 'evar' in ele:
                    return '(%s AS %s)' % (self.ele2str(ele['expr']), self.ele2str(ele['evar']))
            elif ele.name.startswith('Builtin_') and 'arg' in ele:
                return '%s(%s)' % (ele.name[8:], self.ele2str(ele['arg']))
            elif ele.name == 'literal':
                return "'%s'" % (self.list2str(list(ele.values()), self.ele2str))

        elif isinstance(ele, list):
            return self.list2str(ele, self.ele2str)
        return str(ele)

    def triple2str(self, triple):
        if len(triple) == 3:
            out = []
            for x in triple:
                out.append(self.ele2str(x))
            out.append('.')
            return ' '.join(out)
        out = []
        for i in range(0, len(triple), 3):
            out.append(self.triple2str(triple[i:i+3]))
        return '\n'.join(out)

    def tree2str(self, t, indent=' ', depth=0):
        out = []
        if isinstance(t, ParseResults):
            for e in t.asList():
                out.append(self.tree2str(e))
            for k, v in sorted(t.items()):
                out.append(self.tree2str(v))

        elif isinstance(t, CompValue):
            if t.name == 'PrefixDecl'and 'iri' in t:
                pref = t['prefix'] if 'prefix' in t else ''
                out.append('PREFIX %s: %s\n' % (pref, t['iri'].n3()))

            elif t.name.endswith('Query') or t.name.startswith('Sub'):
                ret = []
                for k, v in t.items():
                    if k == 'modifier':
                        ret.append(v)
                    elif k == 'projection':
                        ret.append(self.list2str(v, self.ele2str, joiner=' '))
                    elif k == 'template':
                        ret.append('{%s}' % self.list2str(v, self.triple2str))
                    elif k == 'limitoffset':
                        for k_, v_ in v.items():
                            ret.append('%s %s \n' % (k_.upper(), self.tree2str(v_)))
                    elif k in self.fixed_recursion:
                        ret.append(self.fixed_recursion[k] % (self.tree2str(v)))
                    else:
                        ret.append(self.tree2str(v))
                query_type = t.name[:-5] if t.name.endswith('Query') else t.name[3:]
                out.append('%s %s' % (query_type.upper(), ' '.join(ret)))

            elif t.name == 'TriplesBlock' and 'triples' in t:
                for tri in t['triples']:
                    out.append('%s\n' % (self.triple2str(tri)))
            elif t.name == 'OptionalGraphPattern' and 'graph' in t:
                out.append('\nOPTIONAL { \n%s\n} .\n' % self.tree2str(t['graph']))
            elif t.name == 'GroupOrUnionGraphPattern' and 'graph' in t:
                if len(t['graph']) > 1:
                    ret = []
                    for x in t['graph']:
                        ret.append(self.tree2str(x))
                    out.append('{\n%s\n}' % ('\n} UNION {\n'.join(ret)))
                elif len(t['graph']) == 1:
                    out.append('{\n%s\n}' % self.tree2str(t['graph']))
            elif t.name in ['Filter']:
                out.append('\n%s ( %s ) .\n' % (t.name.upper(), self.ele2str(t['expr'])))

            else:
                for k, v in t.items():
                    # if k == 'order':
                    out.append(self.tree2str(v))
        elif isinstance(t, dict):
            for k, v in t.items():
                out.append(self.tree2str(v))
        elif isinstance(t, list):
            for e in t:
                out.append(self.tree2str(e))
        else:
            out.append("%s " % (self.ele2str(t)))
        return "".join(out)

    @staticmethod
    def list2str(l, method, prefix='', suffix='', joiner='\n'):
        out = []
        for x in l:
            out.append('%s%s%s' % (prefix, method(x), suffix))
        return joiner.join(out)

    @staticmethod
    def pretty_print(query_tree):
        print(prettify_parsetree(query_tree))

