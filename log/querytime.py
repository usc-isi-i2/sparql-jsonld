

from datetime import datetime


def log_querytime(query_name, how_long, endpoint, full_query='', output_file='./querytime.log'):
    try:
        with open(output_file, 'a') as fout:
            record = '{: <35} {: <8} {: <35} {: <30} {}\n'.format(query_name,
                                                                   how_long,
                                                                   endpoint.replace('http://', ''),
                                                                   str(datetime.now()),
                                                                   full_query.replace('\n', '\t'))
            fout.write(record)
    except Exception as e:
        print('fail to log: ', e)
