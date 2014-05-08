import json
import logging
import time
from collections import defaultdict

from Exchange import Exchange

class MintPal(Exchange):
    '''A wrapper for the MintPal exchange API.'''
    # Note, this wrapper uses MintPal's stable v1 api but soon they will
    # upgrade to v2, which is unstable right now

    def __init__(self, exchanges=None):
        '''Grab all coins that can be bought/sold for btc or ltc.
        This can be a lot of coins, so an optional, pre-specified dictionary
        of exchanges to coins can be given in <exchanges>'''

        self.name = 'mintpal'
        self.logger = logging.getLogger(self.name)
        self.host = 'api.mintpal.com'
        self.conn_closed = True
        self.fee = 0.15
        self.movebook = defaultdict(dict)

        if not exchanges:
            self.logger.debug('No exchange dictionary provided.')
            self.logger.debug('Fetching default exchanges and all tradeable coins.')
            # The exchanges they provide as specified at https://www.mintpal.com/api
            self.exchanges = {'btc': [], 'ltc': []}
            self.open_conn()
            for exchange in self.exchanges.keys():
                self.conn.request('GET', '/v1/market/summary/' + exchange)
                response = self.conn.getresponse()
                market_summary = json.load(response)
                # If exchanges was not specified, we grab all coins possible to
                # trade in this exchange
                self.exchanges[exchange] = [str(entry['code'].lower()) for entry in market_summary]
        else:
            self.logger.debug('Using provided exchange dictionary.')
            self.exchanges = exchanges

    def _update_movebook(self):
        self.logger.debug('Updating movebook...')
        for exchange in self.exchanges:
            for coin in self.exchanges[exchange]:
                self.open_conn()
                try:
                    # This request gives us orders of people buying <coin> for
                    # <exchange>, which means we can (almost) immediately sell
                    # <coin> for <exchange>.  <volume> is how much of <coin> we can
                    # sell.
                    self.conn.request('GET', '/v1/market/orders/{}/{}/buy'.format(coin, exchange))
                    response = self.conn.getresponse()
                    buy_order_data = json.load(response)
                    self.movebook[coin][exchange] = [{'price': buy_order['price'], 'volume': buy_order['amount']} for buy_order in buy_order_data['orders']]

                    # This request gives us orders of people selling <coin> for
                    #  <exchange>, which means we can (almost) immediately buy
                    #  <coin> for <exchange>.
                    self.conn.request('GET', '/v1/market/orders/{}/{}/sell'.format(coin, exchange))
                    response = self.conn.getresponse()
                    sell_order_data = json.load(response)
                    self.movebook[exchange][coin] = [{'price': sell_order['price'], 'volume': sell_order['total']} for sell_order in sell_order_data['orders']]
                except Exception as e:
                    # All exceptions that are *non-system-exiting* should
                    # subclass Exception.  Since these are non-fatal, we should
                    # continue to populate the movebook
                    self.logger.warning('Exception thrown during update_movebook.  {}'.format(e))
                    self.logger.debug('Response: status: {}, reason: {}'.format(response.status, response.reason))
                    self.close_conn()
                    # If an exception was thrown during the fetching of
                    # coin/exchange price data, the data from the last update
                    # is still there and is now stale.  Clear it.
                    self.movebook[exchange][coin] = []
                    self.movebook[coin][exchange] = []