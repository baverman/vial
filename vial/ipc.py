from time import time, sleep
from cPickle import dumps
from multiprocessing import connection
from threading import Lock, Thread

from multiprocessing.connection import Listener

def arbitrary_address(family=None):
    return connection.arbitrary_address(family or connection.default_family)

class Server(object):
    def __init__(self, conn, logger=None):
        self.conn = conn
        self.logger = logger

    def _process(self, name, args, kwargs):
        try:
            is_ok = True
            result = getattr(self, name)(*args, **kwargs)
        except Exception as e:
            if self.logger:
                self.logger.exception('Call exception')

            is_ok = False
            result = e.__class__.__name__, str(e)

        return is_ok, result

    def run(self):
        conn = self.conn
        while True:
            if conn.poll(1):
                try:
                    args = conn.recv()
                except EOFError:
                    break
                except:
                    if self.logger:
                        self.logger.exception('Recv exception')
                    break

                if args[0] == 'close':
                    conn.close()
                    break
                else:
                    result = self._process(*args)
                    try:
                        self.conn.send_bytes(dumps(result, 2))
                    except:
                        if self.logger:
                            self.logger.exception('Send exception')

class Connection(object):
    def __init__(self, address, start_timeout=5):
        self.address = address
        self.start_timeout = start_timeout
        self.prepare_thread = None
        self.prepare_lock = Lock()

    def _run(self):
        start = time()
        while True:
            try:
                self.conn = connection.Client(self.address)
            except Exception, e:
                if time() - start > self.start_timeout:
                    raise Exception('Server launch timeout: ' + str(e))

                sleep(0.3)
            else:
                break

    def _threaded_run(self):
        try:
            self._run()
        finally:
            self.prepare_thread = None

    def prepare(self):
        with self.prepare_lock:
            if self.prepare_thread:
                return

            if hasattr(self, 'conn'):
                return

            self.prepare_thread = Thread(target=self._threaded_run)
            self.prepare_thread.start()

    def run(self):
        with self.prepare_lock:
            if self.prepare_thread:
                self.prepare_thread.join()

            if not hasattr(self, 'conn'):
                self._run()

    def get(self):
        try:
            return self.conn
        except AttributeError:
            self.run()

        return self.conn


class Client(object):
    def __init__(self, conn):
        self.conn = conn

    def _call(self, name, *args, **kwargs):

        self.conn.get().send_bytes(dumps((name, args, kwargs), 2))

        if name == 'close':
            return

        is_ok, result = self.conn.get().recv()
        if is_ok:
            return result
        else:
            raise Exception(result)

    def __getattr__(self, name):
        def inner(*args, **kwargs):
            return self._call(name, *args, **kwargs)

        inner.__name__ = name
        self.__dict__[name] = inner
        return inner