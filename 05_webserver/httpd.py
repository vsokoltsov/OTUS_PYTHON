import logging
import multiprocessing
import argparse
import ipdb

from server import HttpServer

WORKERS_COUNT = 1
LOGGING_FORMAT = "'[%(asctime)s] %(levelname).1s %(message)s'"
LOGGING_DATE_FORMAT = "'%Y.%m.%d %H:%M:%S'"

def start_server(root_path):
    """ Create server instance and forever run it """

    try:
        server = HttpServer(document_root=root_path)
        server.run_forever()
    except KeyboardInterrupt:
        logging.info('Server exited')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get config file')
    logging.basicConfig(
        format=LOGGING_FORMAT, datefmt=LOGGING_DATE_FORMAT, level=logging.INFO
    )
    parser.add_argument('-w', type=int, help='Number of workers')
    parser.add_argument('-r', type=str, help='Root path of the documents')

    params = parser.parse_args()
    workers = params.w or WORKERS_COUNT
    document_root = params.r or None
    for _ in range(workers):
        p = multiprocessing.Process(target=start_server, args=(document_root,))
        p.start()
