

from datetime import datetime


def log_querytime(query_name, res_len, bucket_len, time_query, time_frame, endpoint, full_query='', output_file='./info.log'):
    try:
        with open(output_file, 'a') as fout:
            record = '{: <35} {: <8} {: <8} {: <8} {: <8} {: <35} {: <30} {}\n'.format(query_name,
                                                                                res_len,
                                                                                bucket_len,
                                                                                int(time_query),
                                                                                int(time_frame),
                                                                                endpoint.replace('http://', ''),
                                                                                str(datetime.now()),
                                                                                full_query.replace('\n', '\t'))
            fout.write(record)
    except Exception as e:
        print('fail to log: ', e)
