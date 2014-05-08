import json
import urllib
import logging
from collections import defaultdict

from Exchange import Exchange

class Poloniex(Exchange):

    def __init__(self, exchanges=None):
        self.name = 'poloniex'
        self.logger = logging.getLogger(self.name)
        self.host = 'poloniex.com'
        self.conn_closed = True
        self.fee = 0.15
        self.movebook = defaultdict(dict)

        if not exchanges:
            self.exchanges = defaultdict(list)
            self.logger.debug('No exchange dictionary provided.')
            self.logger.info('Fetching default exchanges and all tradeable coins.')
            self.logger.warning('This is not recommended as movebook updates will be slow.')
            self.open_conn()
            self.conn.request('GET', '/public?command=returnTicker')
            response = self.conn.getresponse()
            ticker_pairs = json.load(response)
            for ticker_pair in ticker_pairs.keys():
                exchange, coin = ticker_pair.split('_')
                self.exchanges[exchange].append(coin)
        else:
            self.logger.info('Using provided exchange dictionary.')
            self.exchanges = exchanges

    def _update_move(self, exchange, coin):
        self.logger.info('Updating moves between {} and {}...'.format(exchange, coin))
        self.conn.request('GET', '/public?command=returnOrderBook&currencyPair={}_{}'.format(exchange, coin))
        response = self.conn.getresponse()
        data = json.load(response)
        self.movebook[exchange][coin] = [{'price': float(ask[0]), 'volume': float(ask[0])*float(ask[1])} for ask in data['asks']]
        self.movebook[coin][exchange] = [{'price': float(bid[0]), 'volume': float(bid[1])} for bid in data['bids']]
