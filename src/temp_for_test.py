
# To REWRITE
def select2construct(select_query, frame):

    def recur(root, parent, statements):
        for k, v in root.items():
            if not k.startswith('@'):
                new_var = '?' + k.split(':')[-1]
                statements.append(parent + ' ' + k + ' ' + new_var + ' .')
                if isinstance(v, dict) and len(v):
                    recur(v, new_var, statements)

    statements = ['?main rdf:type ' + frame['@type'] + ' .']

    recur(frame, '?main', statements)

    ori = select_query.split('\n')
    new_query = []
    i = 0
    while i < len(ori):
        q = ori[i]
        if q:
            if q.startswith('PREFIX'):
                new_query.append(q)
                i += 1
            elif q.startswith('SELECT'):
                new_query.append('CONSTRUCT {')
                for s in statements:
                    new_query.append('\t' + s)
                new_query.append('}')
                while not ori[i].startswith('WHERE'):
                    i += 1
            else:
                while i < len(ori) and not ori[i].startswith('}'):
                    new_query.append(ori[i])
                    i += 1
                for s in statements:
                    if '  ' + s not in new_query:
                        # new_query.append('  OPTIONAL {' + s + '} .') # should be optional
                        new_query.append('  ' + s)
                while i < len(ori):
                    new_query.append(ori[i])
                    i += 1
                break
        else:
            i += 1

    return '\n'.join(new_query)
