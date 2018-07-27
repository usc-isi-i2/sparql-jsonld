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

    def query(self, query: str, frame: dict=None, context: dict=None, optional: bool=True) -> dict:
        """
        Take in a SPARQL query and return the final nested results as a list of json objects
        :param query: a SPARQL query string
        :param frame: a json frame
        :param context: context for the frame in json
        :param optional: if the extra fields in the frame is optional, default to be true(optional)
        :return: a dict holding nested json-ld results
        """

        if frame:
            if '@context' in context:
                context = context['@context']

            frame = self.remove_a(frame, context)

            # parse and update the query by the frame:
            print('- parse query\ttime: %s' % time.time())
            q = SPARQLQuery(query)
            updater = Updater(context)

            print('- update query\ttime: %s' % time.time())
            subjects = q.get_limit_subjects(graph=self.graph)
            q.update_query_by_frame(updater, frame, optional=optional, specified_subjects=subjects)

            # print(q.str_query)
            # q.pprint_tree()

            # query with the updated query:
            print('- send query\ttime: %s' % time.time())
            self.graph.setQuery(q.str_query)
            self.graph.setReturnFormat(JSONLD)
            try:
                res = self.graph.query().convert().serialize(format='json-ld').decode('utf-8')

                print('- frame result\ttime: %s' % time.time())

                frame_with_context = {
                    '@context': updater.context,
                    **frame
                }

                if res == '[]':
                    return {'@error': 'Empty Result'}
                # print(res)

                framed = jsonld.frame(json.loads(res),
                                      frame_with_context,
                                      options={
                                          'embed': '@always'
                                      })

                print('- all done . \ttime: %s' % time.time())
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
            self.graph.setQuery(query)
            self.graph.setReturnFormat(JSON)
            res = self.graph.query().convert()
            return {'@graph': res}

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


