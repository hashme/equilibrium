import httplib
import json
import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

class MintPal:
    '''A wrapper for the MintPal exchange API.'''
    # Note, this wrapper uses MintPal's stable v1 api but soon they will
    # upgrade to v2, which is unstable right now

    def initialize(self, exchanges=None):
        '''Grab all coins that can be bought/sold for btc or ltc.
        This can be a lot of coins, so an optional, pre-specified dictionary
        of exchanges to coins can be given in <exchanges>'''

        self.name = 'mintpal'
        self.logger = logging.getLogger(self.name)
        self.fee = 0.15
        self.conn = httplib.HTTPSConnection('api.mintpal.com')
        self.movebook = {}
        if not exchanges:
            self.logger.debug('No exchange dictionary provided.')
            self.logger.debug('Fetching default exchanges and all tradeable coins.')
            # The exchanges they provide as specified at https://www.mintpal.com/api
            self.exchanges = {'btc': [], 'ltc': []}
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
        for exchange in self.exchanges.keys():
            self.movebook[exchange] = {}
            for coin in self.exchanges[exchange]:
                self.movebook[coin] = {}
                self.movebook[coin][exchange] = {'price': 0.00, 'volume': 0.00, 'fee': 0.00}
                self.movebook[exchange][coin] = {'price': 0.00, 'volume': 0.00, 'fee': 0.00}

    def balance(self):
        # Returns balance, which looks like {'BTC_EXCHANGE':0.82,'LTC_EXCHANGE':10.34}
        pass

    def trade(self, currency_from, currency_to, ratio, amount):
        # Executes trade corresponding to orderbook[currency_from][currency_to] = {'ratio':ratio,'volume':amount}
        # Blocks until trade is complete.
        pass

    def withdraw(self, currency, amount, address):
        # Transfers currency (e.g, "BTC_EXCHANGE") in amount amount to external address address.
        pass

    def update_movebook(self):
        try:
            self.logger.debug('Updating movebook...')
            for exchange in self.exchanges:
                for coin in self.exchanges[exchange]:
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
        except ValueError as e:
            self.logger.warning('ValueError thrown during update_movebook.  Possible rate-limit exceeded. {}'.format(e))
    def run(self):
        while(True):
            self.update_movebook()

    def cleanup(self):
        self.conn.close()