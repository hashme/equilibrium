import json
from collections import defaultdict

from Exchange import Exchange

class Bter(Exchange):
    '''A wrapper for the BTER exchange API.'''

    def __init__(self, exchanges=None):
        self.name = 'bter'
        self.logger = logging.getLogger(self.name)
        self.host = 'data.bter.com'
        self.conn_closed = True
        self.fee = 0.2
        self.movebook = defaultdict(dict)

        if not exchanges:
            self.exchanges = defaultdict(list)
            self.logger.debug('No exchange dictionary provided.')
            self.logger.debug('Fetching default exchanges and all tradeable coins.')
            self.open_conn()
            self.conn.request('GET', '/api/1/tickers')
            response = self.conn.getresponse()
            ticker_pairs = json.load(response)
            for ticker_pair in ticker_pairs.keys():
                coin, exchange = ticker_pair.split('_')
                self.exchanges[exchange].append(coin)
        else:
            self.logger.debug('Using provided exchange dictionary.')
            self.exchanges = exchanges

    def _update_movebook(self):
        self.logger.debug('Updating movebook...')
        for exchange in self.exchanges:
            for coin in self.exchanges[exchange]:
                self.open_conn()
                try:
                    self.conn.request('GET', '/api/1/depth/{}_{}'.format(coin, exchange))
                    response = self.conn.getresponse()
                    data = json.load(response)
                    # bter always return the price and then volume in terms of
                    # *coin*.  In this first case, we want to know the maximum
                    # exchange we can convert.  This can be found from
                    # price * volume_of_coin = volume of exchange.
                    self.movebook[exchange][coin] = [{'price': float(ask[0]), 'volume': float(ask[0])*float(ask[1])} for ask in data['asks']]
                    self.movebook[coin][exchange] = [{'price': float(bid[0]), 'volume': float(bid[1])} for bid in data['bids']]
                except Exception as e:
                    # All exceptions that are *non-system-exiting* should
                    # subclass Exception.  Since these are non-fatal, we should
                    # continue to populate the movebook
                    self.logger.warning('Exception thrown during update_movebook.  {}'.format(e))
                    self.close_conn()
                    # If an exception was thrown during the fetching of
                    # coin/exchange price data, the data from the last update
                    # is still there and is now stale.  Clear it.
                    self.movebook[exchange][coin] = []
                    self.movebook[coin][exchange] = []


