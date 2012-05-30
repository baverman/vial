from __future__ import absolute_import

import logging
logger = logging.getLogger('vial.vim.server')

import vim

import sys
import os.path

from cPickle import dumps


if __name__ == '__main__':
    import os
    from multiprocessing.connection import Listener
    import logging

    if 'SUPP_LOG_LEVEL' in os.environ:
        level = int(os.environ['SUPP_LOG_LEVEL'])
    else:
        level = logging.ERROR

    logger = logging.getLogger('supplement')
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(name)s %(levelname)s: %(message)s"))
    logger.addHandler(handler)

    listener = Listener(sys.argv[1])
    conn = listener.accept()
    server = Server(conn)
    server.run()
