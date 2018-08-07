from SPARQLWrapper import SPARQLWrapper, JSONLD, JSON, SPARQLExceptions
from pyld import jsonld
import json, time

from .sparql_query import SPARQLQuery
from .updater import Updater


class QueryWrapper(object):
    """
    A Starter is used for initializing an endpoint to graph and do the SPARQL queries.
    """

    def __init__(self, database: str) -> None:
        """
        Init a starter with address of a database
        :param database: str - query endpoint of the database

        """

        self.graph = SPARQLWrapper(database)

    def query(self, query: str, frame: dict=None, context: dict=None, optional: bool=True, paging=0) -> dict:
        """
        Take in a SPARQL query and return the final nested results as a list of json objects
        :param query: a SPARQL query string
        :param frame: a json frame
        :param context: context for the frame in json
        :param optional: if the extra fields in the frame is optional, default to be true(optional)
        :param paging: limit per query, default 0 means no limit
        :return: a dict holding nested json-ld results
        """

        if frame:
            if '@context' in context:
                context = context['@context']

            frame = self.remove_a(frame, context)

            # parse and update the query by the frame:
            ori_q = SPARQLQuery(query)
            updater = Updater(context)

            subjects = ori_q.get_limit_subjects(graph=self.graph)

            try:

                start_query = time.time()
                if paging:
                    res = []
                    ss = [subjects[i:i + paging] for i in range(0, len(subjects), paging)]
                    for s in ss:
                        q = SPARQLQuery(query)
                        q.update_query_by_frame(updater, frame, optional=optional, specified_subjects=s)
                        res += json.loads(self.query_single_construct(q))
                else:
                    ori_q.update_query_by_frame(updater, frame, optional=optional, specified_subjects=subjects)
                    res = json.loads(self.query_single_construct(ori_q))

                time_query = time.time() - start_query

                frame_with_context = {
                    '@context': updater.context,
                    **frame
                }

                if res == '[]':
                    return {'@graph': [], '@info': self.wrap_info(0, -1, time_query, -1)}
                # print(res)

                start_frame = time.time()
                framed = jsonld.frame(res,
                                      frame_with_context,
                                      options={
                                          'embed': '@always'
                                      })

                time_frame = time.time() - start_frame
                framed['@info'] = self.wrap_info(len(framed.get('@graph', {})), -1, time_query, time_frame)
                return framed
            except jsonld.JsonLdError as e:
                return {'@error': 'Framing Error: %s' % e}
            except SPARQLExceptions.EndPointInternalError as e:
                return {'@error': 'Query Error: %s' % e}
            except SPARQLExceptions.EndPointNotFound as e:
                return {'@error': 'Query Error: %s' % e}
            except SPARQLExceptions.QueryBadFormed as e:
                return {'@error': 'Bad Query: %s' % e}
            except KeyError as e:
                return {'@error': 'KeyError: %s' % e}
            except IndexError as e:
                return {'@error': 'IndexError: %s' % e}
            except Exception as e:
                return {'@error': 'Exception: %s' % e}

        # no frame, just send the original query to the endpoint:
        else:
            start_query = time.time()
            self.graph.setQuery(query)
            self.graph.setReturnFormat(JSON)
            res = self.graph.query().convert()
            time_query = time.time() - start_query
            len_buckets = len(res.get('results', {}).get('bindings', {}))
            return {'@graph': res, '@info': self.wrap_info(-1, len_buckets, time_query, -1)}

    def query_single_construct(self, q):
        # print(q.str_query)
        # q.pprint_tree()

        # query with the updated query:
        self.graph.setQuery(q.str_query)
        self.graph.setReturnFormat(JSONLD)

        return self.graph.query().convert().serialize(format='json-ld').decode('utf-8')

    def remove_a(self, frame, context):
        target = {}
        for k, v in frame.items():
            if k in context and '@container' in context[k]:
                if context[k]['@container'] == '@index':
                    # TODO: solve "@contianer": "@index"
                    # target[k] = v if v else {'': ''}
                    print('ignore "@contianer": "@index" in %s.' % k)
                    del context[k]['@container']
            if k != 'a':
                # TODO: solve "a": "@type" -> key collision with "@type"
                if isinstance(v, dict) and 'a' in v and '@type' in v:
                    target[k] = self.remove_a(v, context)
                else:
                    target[k] = v
        return target

    @staticmethod
    def wrap_info(len_results, len_buckets, time_query, time_frame):
        return {
            'len_results': len_results,
            'len_buckets': len_buckets,
            'time_query': time_query,
            'time_frame': time_frame
        }


