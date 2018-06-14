from pyquery import PyQuery as pq
import file_operation
import sys
import summary
import id_add
import re
import logging
import redisdb


def log(func):
    def wrapper():
        logging.basicConfig(filename='CoStar_log.log', level=logging.DEBUG)
        return func
    return wrapper


# @log
def main():

    logging.basicConfig(filename='CoStar_log.log', level=logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter("%(message)s"))
    logging.getLogger().addHandler(console)

    folder_name = 'Offices'
    # folder_name = 'Multifamily'
    file_id = "020-1.html"

    file_path = r'F:/code_test/CoStar_Project/2018_5_25_new_source_files/' \
                r'{0}/{1}'.format(folder_name, file_id)
    logging.info(file_path)

    file = file_operation.file_read(file_path)
    doc = pq(file)

    file_id = re.match(r".*(?=.htm)", file_id).group()

    s = summary.Summary(doc, file_id)
    a = s.assessment()

    logging.info('=====>')
    # logging.info("file file_id is:", file_id)
    logging.info("file_id is: {}".format(file_id))
    # logging.info("main.py type(a) ->", type(a))
    logging.info("main.py type(a) -> {}".format(type(a)))
    # logging.info(dict(a))
    logging.info("{}".format(dict(a)))
    logging.info('=====>')
    # logging.info("file_id is:", file_id)
    logging.info("file_id is: {}".format(file_id))
    logging.info('main.py result --->')
    # logging.info(s.result)
    # logging.info("{}".format(s.result).encode('utf-8'))
    logging.info(s.result.__str__().encode('utf-8'))

    # Save results in Redis Database.
    redisdb.save_in_redis('Summary', s.result, 0)


if __name__ == '__main__':
    main()

