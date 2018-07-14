import json


class NestedRDF(object):
    def __init__(self, rdf: str):
        if isinstance(rdf, bytes):
            self._data = rdf.decode('utf-8')
        else:
            self._data = rdf
        self._nested_jsonld = self.nest_data(rdf)

    @property
    def original_data(self):
        if isinstance(self._data, bytes):
            return self._data.decode('utf-8')
        return self._data

    @property
    def nested_jsonld(self):
        return self._nested_jsonld

    @staticmethod
    def nest_data(rdf: str):
        """
        Parse the flatten RDF data to a list of nested json objects
        """

        try:

            # may only supply to the serialized rdflib.query.Result in json-ld

            ori = json.loads(rdf)
            mapping = {}
            for rec in ori:
                if '@id' in rec:
                    mapping[rec['@id']] = rec

            to_del = set()

            def insert_value(source, target):
                if isinstance(source, dict) and isinstance(target, dict):
                    for k, v in source.items():
                        if k in target:
                            insert_value(source[k], target[k])
                        else:
                            target[k] = v

            def fill_a_record(record):
                if isinstance(record, dict) and '@id' in record:
                    for k, v in record.items():
                        if not k.startswith('@'):
                            if isinstance(v, list):
                                for i in range(len(v)):
                                    if '@id' in v[i] and v[i]['@id'] in mapping:
                                        insert_value(mapping[v[i]['@id']], v[i])
                                        to_del.add(v[i]['@id'])
                            elif isinstance(v, dict):
                                if '@id' in v and v['@id'] in mapping:
                                    insert_value(mapping[v['@id']], v)
                                    to_del.add(v['@id'])

            for rec in ori:
                fill_a_record(rec)

            for x in to_del:
                del mapping[x]

            return list(mapping.values())
        except Exception as e:
            print('Exception when nest data: ', e)
            return []
