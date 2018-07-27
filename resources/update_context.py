import os, json


with open('karma_context.json') as f:
    context = json.load(f)['@context']


def to_obj(name):
    if name not in context:
        print('%s not in context ' % name)
    elif isinstance(context[name], dict) and context[name].get('@type', '') != '@id':
        context[name]['@type'] = '@id'


def to_literal(name):
    if name not in context:
        print('%s not in context ' % name)
    elif isinstance(context[name], dict) and context[name].get('@type') == '@id':
        del context[name]['@type']


owl = set()
owl_datatype = set()

with open('../../gaia_files/schemaorg.owl') as f:
    import re
    texts = f.read()
    x = re.findall(r'(?<=<owl:Class rdf:about=")(.+)(?:")', texts)
    x_ = re.findall(r'(?<=<owl:ObjectProperty rdf:about=")(.+)(?:")', texts)
    x__ = re.findall(r'(?<=<owl:datatypeProperty rdf:about=")(.+)(?:")', texts)
    for y in x:
        owl.add(y.split('/')[-1])
    for y in x_:
        owl.add(y.split('/')[-1])
    for y in x__:
        owl_datatype.add(y.split('/')[-1])


dig = set()
dig_datatype = set()

def check_class(fp):
    with open(fp) as f:
        import re
        terms = f.read().split('.\n\n')
        for t in terms:
            if re.search('(?<=memex:)([a-zA-Z0-9_]+)(?=  ?a owl:Class)', t):
                name = re.search('(?<=memex:)([a-zA-Z0-9_]+)(?=  ?a owl:Class)', t).group()
                dig.add(name)
            elif re.search('(?<=memex:)([a-zA-Z0-9_]+)(?= rdf:type owl:Class)', t):
                name = re.search('(?<=memex:)([a-zA-Z0-9_]+)(?= rdf:type owl:Class)', t).group()
                dig.add(name)


def check_property(fp):
    with open(fp) as f:
        import re
        terms = f.read().split('.\n\n')
        for t in terms:
            if re.search('(?<=memex:)([a-zA-Z0-9_]+)(?=  ?a  ?rdf:Property)', t) and re.search('(?<=schema:rangeIncludes )([a-zA-Z]+):([a-zA-Z0-9_]+)(?= ?;)', t):
                name = re.search('(?<=memex:)([a-zA-Z0-9_]+)(?=  ?a  ?rdf:Property)', t).group()
                prefix, localname = re.search('(?<=schema:rangeIncludes )([a-zA-Z]+):([a-zA-Z0-9_]+)(?= ?;)', t).groups()
                if localname in ['Boolean', 'Date', 'DateTime', 'Number', 'Integer', 'Text', 'Time', 'Literal']:
                    dig_datatype.add(name)
                else:
                    dig.add(name)


f1 = '../../gaia_files/dig_ontologies.ttl'

check_class(f1)
check_property(f1)


empty_value_key = set() # all in dig_ont
obj_value_key = set()   # all in ont no one in dig_ont
obj_value_type = set()  # must be @type:@id anyway, all in ont no one in dig_ont


def check(root):
    for k, v in root.items():
        if isinstance(v, dict) and v:
            obj_value_key.add(k)
            check(v)
        elif k == '@type':
            obj_value_type.add(v)
        else:
            empty_value_key.add(k)


for filename in os.listdir('frames'):
    with open('frames/%s' % filename) as f:
        frame = json.load(f)
        check(frame)


dig_ont = set()
ont = set()
for k, v in context.items():
    if isinstance(v, dict):
        if re.findall(r'dig\.isi\.edu', v.get('@id')):
            dig_ont.add(k)
            continue
    ont.add(k)

in_frame_obj = obj_value_type.union(obj_value_key).difference({'username'})
in_frame_literal = empty_value_key.difference({'vendor', 'seller'})

unknown_dig = set()
unknown_org = set()
for c in context:
    if c in in_frame_literal:
        to_literal(c)
    elif c in in_frame_obj:
        to_obj(c)
    elif c in ont and c in owl:
        to_obj(c)
    elif c in ont and c in owl_datatype:
        to_obj(c)
    elif c in dig:
        to_obj(c)
    elif c in dig_datatype:
        to_literal(c)

    # schema.org ontology but not in owl and frame ?
    # dig ontology but not in frame
    else:
        if c in dig_ont:
            unknown_dig.add(c)
        else:
            unknown_org.add(c)


print(unknown_org)
# unknown_org: start with uppercase->@id, lowercase->@value

print(len(unknown_dig), unknown_dig)

with open('new_context.json', 'w') as f:
    json.dump(fp=f, obj={'@context': context}, indent=4)

