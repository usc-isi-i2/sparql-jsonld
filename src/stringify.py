from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.term import URIRef, Literal, BNode, Variable
from pyparsing import ParseResults

# TODO: refactor, support [], functions, graph etc.

fixed_recursion = {
        'where': '\nWHERE { \n%s\n}\n',
        'orderby': 'ORDER BY %s\n',
        'groupby': 'GROUP BY %s\n',
        'datasetClause': 'FROM %s'
    }


def ele2str(ele: object) -> str:
    if isinstance(ele, Literal):
        try:
            val = int(ele)
            return str(val)
        except ValueError:
            return '"%s"' % ele
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
            return ele2str(ele['part'])
        elif ele.name.endswith('Expression'):
            if len(ele) == 1 and 'expr' in ele:
                return ele2str(ele['expr'])
            elif ele.name == 'ConditionalAndExpression':
                return list2str([ele['expr']] + ele.get('other', []), ele2str, joiner=' && ')
            elif ele.name == 'AdditiveExpression':
                return '(%s)' % list2str(list(ele.values()), ele2str, joiner=' ')
            else:
                return list2str(list(ele.values()), ele2str, joiner=' ')
        elif ele.name == 'UnaryNot' and 'expr' in ele:
            return '!%s' % (ele2str(ele['expr']))
        elif ele.name.startswith('Aggregate_'):
            return '%s(%s)' % (ele.name[10:].upper(), ele2str(ele['vars']))
        elif ele.name == 'vars':
            if 'var' in ele:
                return ele2str(ele['var'])
            elif 'expr' and 'evar' in ele:
                return '(%s AS %s)' % (ele2str(ele['expr']), ele2str(ele['evar']))
        elif ele.name.startswith('Builtin_'):
            if 'arg' in ele:
                return '%s(%s)' % (ele.name[8:], ele2str(ele['arg']))
            elif 'text' and 'pattern' in ele:
                return '%s(%s, %s)' % (ele.name[8:], ele2str(ele['text']), ele2str(ele['pattern']))
        elif ele.name == 'literal':
            return '"%s"' % (list2str(list(ele.values()), ele2str)).strip("'").strip('"')
        elif ele.name == 'Function' and 'iri' in ele and 'expr' in ele:
            return '%s(%s)' % (ele2str(ele['iri']), ele2str(ele['expr']))

    elif isinstance(ele, list):
        return list2str(ele, ele2str)
    return str(ele)


def list2str(l: list, method: staticmethod, prefix: str='', suffix: str='', joiner: str='\n') -> str:
    out = []
    for x in l:
        out.append('%s%s%s' % (prefix, method(x), suffix))
    return joiner.join(out)


def triple2str(triple: list or tuple) -> str:
    if len(triple) == 3:
        out = []
        for x in triple:
            out.append(ele2str(x))
        out.append('.')
        return ' '.join(out)
    out = []
    for i in range(0, len(triple), 3):
        out.append(triple2str(triple[i:i+3]))
    return '\n'.join(out)


def tree2str(t: ParseResults) -> str:
    out = []
    if isinstance(t, ParseResults):
        for e in t.asList():
            out.append(tree2str(e))
        for k, v in sorted(t.items()):
            out.append(tree2str(v))

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
                    ret.append(list2str(v, ele2str, joiner=' '))
                elif k == 'template':
                    ret.append('{%s}' % list2str(v, triple2str))
                elif k == 'limitoffset':
                    for k_, v_ in v.items():
                        ret.append('%s %s \n' % (k_.upper(), tree2str(v_)))
                elif k in fixed_recursion:
                    ret.append(fixed_recursion[k] % (tree2str(v)))
                else:
                    ret.append(tree2str(v))
            query_type = t.name[:-5] if t.name.endswith('Query') else t.name[3:]
            out.append('%s %s' % (query_type.upper(), ' '.join(ret)))

        elif t.name == 'TriplesBlock' and 'triples' in t:
            for tri in t['triples']:
                out.append('%s\n' % (triple2str(tri)))
        elif t.name == 'OptionalGraphPattern' and 'graph' in t:
            out.append('OPTIONAL {%s} .\n' % tree2str(t['graph']))
        elif t.name == 'InlineData' and 'var' in t and 'value' in t:
            out.append('Values (%s) {%s} .\n' % (ele2str(t['var']),
                                                  list2str(t['value'], ele2str, prefix='(', suffix=')', joiner='\n')))
        elif t.name == 'GroupOrUnionGraphPattern' and 'graph' in t:
            if len(t['graph']) > 1:
                ret = []
                for x in t['graph']:
                    ret.append(tree2str(x))
                out.append('{\n%s\n}' % ('\n} UNION {\n'.join(ret)))
            elif len(t['graph']) == 1:
                out.append('{\n%s\n}' % tree2str(t['graph']))
        elif t.name in ['Filter']:
            out.append('\n%s ( %s ) .\n' % (t.name.upper(), ele2str(t['expr'])))
        elif t.name == 'OrderCondition' and 'order' in t and 'expr' in t:
            out.append('%s(%s)' % (ele2str(t['order']), ele2str(t['expr'])))

        else:
            for k, v in t.items():
                out.append(tree2str(v))
    elif isinstance(t, dict):
        for k, v in t.items():
            out.append(tree2str(v))
    elif isinstance(t, list):
        for e in t:
            out.append(tree2str(e))
    else:
        out.append("%s " % (ele2str(t)))
    return "".join(out)


def stringify(query_tree: ParseResults) -> str:
    if isinstance(query_tree, ParseResults):
        return tree2str(query_tree)




