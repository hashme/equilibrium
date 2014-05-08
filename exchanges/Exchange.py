import logging
import httplib
logging.basicConfig(format='%(asctime)s %(name)s: %(message)s', level=logging.DEBUG)

class Exchange:

    def open_conn(self):
        if self.conn_closed:
            self.logger.debug('Opening new connection.')
            self.conn = httplib.HTTPSConnection(self.host)
            self.conn_closed = False

    def close_conn(self):
        if not self.conn_closed:
            self.logger.debug('Closing connection.')
            self.conn.close()
            self.conn_closed = True

    def cleanup(self):
        self.logger.debug('Cleaning up.')
        self.close_conn()

    def run(self):
        try:
            while(True):
                self._update_movebook()
        except KeyboardInterrupt:
            self.logger.debug('Caught KeyboardInterrupt.')
            self.close_conn()

    def __init__(self):
        raise NotImplementedError('Must implement init.')

    def _update_movebook(self):
        raise NotImplementedError('Must implement init.')