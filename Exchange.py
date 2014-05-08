import urllib
import urllib2
import httplib
import hashlib
import hmac
import time
import json
import functools
from multiprocessing import Process, Lock

DEBUG = True

class Exchange:
    '''An interface that specific exchange objects implement.
    Used to consistently update the orderbook.'''

    def lprint(self,text):
        with self.printlock:
            print text
    def initialize(self):
        # Is called to initialize this module.
        # Recommend setting self.conn and all instance variables.
        self.name = 'EXCHANGE'
    def balance(self):
        # Returns balance, which looks like {'BTC_EXCHANGE':0.82,'LTC_EXCHANGE':10.34}
        pass
    def trade(self, currency_from, currency_to, ratio, amount):
        # Executes trade corresponding to orderbook[currency_from][currency_to] = {'ratio':ratio,'volume':amount}
        # Blocks until trade is complete.
        pass
    def transfer(self, currency, amount, address):
        # Transfers currency (e.g, "BTC_EXCHANGE") in amount amount to external address address.
        pass
    def frame(self):
        # Is called very often and must return orderbook.
        # orderbook[CUR_1][CUR_2] = {'ratio':ratio,'cost':cost,'volume':volume}
        # If we start with volume of CUR_1, we can instantly turn it into (ratio*volume)-cost of CUR_2.
        # Conversion from cost in terms of CUR_1 before trade to cost in terms of CUR_2 after trade
        # (which is what we want) is cost_in_CUR_1_before_trade * ratio = cost_in_CUR_2_after_trade.
        pass
    def cleanup(self):
        # Called on exit. self.conn.close()?
        pass
    def run(self):
        self.initialize()
        while True:
            try:
                self.update(self.frame())
            except KeyboardInterrupt:
                self.lprint('! CAUGHT KEYBOARD INTERRUPT')
                break
            except Exception as e:
                self.lprint('! ERROR GRABBING DATA IN EXCHANGE {0}'.format(self.name))
                self.lprint('! ' + str(e))
                if DEBUG:raise
        self.cleanup()
    def __init__(self, update, printlock):
        self.update = update
        self.printlock = printlock
        p = Process(target = self.run)
        p.start()

class BTCE(Exchange):
    def getNonce(self):
        nonce = ''
        try:
            f_h = open('btcenonce.dat')
            nonce = int(f_h.read())+1
            f_h.close()
        except:
            nonce = int(time.time())
        f_h = open('btcenonce.dat','w')
        f_h.write(str(nonce))
        f_h.close()
        return str(nonce)
    def initialize(self):
        self.name = 'BTCE'
        self.BTC_api_key = "E7UP1XGZ-YVSGL06A-1IIMJBLC-EQFQT2JV-DY4QED4H"
        self.BTC_api_secret = "59445bb18d7a33cc40f803a2a72f7ac2e687ccd11ddbd8e5843be56b30eb5755"
        self.forbidden_currencies = ['USD','CNH','EUR','GBP','RUR']
        self.conn = httplib.HTTPSConnection("btc-e.com")
        self.conn.request("GET","/api/3/info")
        response = json.load(self.conn.getresponse())
        self.fees = dict(map(lambda i: (i[0],float(i[1]['fee'])/100.),response['pairs'].items()))
        self.pairs = []
        self.currencies = []
        for pair in self.fees.keys():
            CUR_1,CUR_2 = pair.upper().split('_')
            if CUR_1 in self.forbidden_currencies or CUR_2 in self.forbidden_currencies:
                continue
            self.pairs.append(pair)
            self.currencies.append(CUR_1)
            self.currencies.append(CUR_2)
    def balance(self):
        H = hmac.new(self.BTC_api_secret, digestmod=hashlib.sha512)
        nonce = self.getNonce()
        params = {"method":"getInfo","nonce":nonce}
        params = urllib.urlencode(params)
        H.update(params)
        sign = H.hexdigest()
        headers = {"Content-type":"application/x-www-form-urlencoded","Key":self.BTC_api_key,"Sign":sign}
        self.conn.request("POST","/tapi",params,headers)
        response = self.conn.getresponse()
        funds = json.load(response)['funds']
        return dict(map(lambda i:(i[0].upper()+'_BTCE',i[1]),funds))
    def trade(self, currency_from, currency_to, ratio, amount):
        pass
    def transfer(self, currency, amount, address):
        pass
    def frame(self):
        orderbook = dict([(CUR+'_BTCE',{}) for CUR in self.currencies])
        orderbook = dict([(CUR+'_BTCE',orderbook.copy()) for CUR in self.currencies])
        self.conn.request("GET","/api/3/depth/"+'-'.join(self.pairs))
        response = json.load(self.conn.getresponse())
        for pair,data in response.items():
            CUR_1,CUR_2 = map(lambda x:x+'_BTCE',pair.upper().split('_'))
            asks = data['asks']
            bids = data['bids']
            orderbook[CUR_1][CUR_2] = []
            # Fees aren't being taken into account - eventually they should be; put them into cost.
            for ratio,volume in bids:
                orderbook[CUR_1][CUR_2].append({'cost':0.0,'ratio':ratio,'volume':volume})
            orderbook[CUR_2][CUR_1] = []
            for ratio,volume in asks:
                orderbook[CUR_2][CUR_1].append({'cost':0.0,'ratio':1.0/ratio,'volume':float(volume)*ratio})
        return orderbook
    def cleanup(self):
        self.conn.close()

class BITFINEX(Exchange):
    def getNonce(self):
        nonce = ''
        try:
            f_h = open('bitfinexnonce.dat')
            nonce = int(f_h.read())+1
            f_h.close()
        except:
            nonce = int(time.time())
        f_h = open('bitfinexnonce.dat','w')
        f_h.write(str(nonce))
        f_h.close()
        return str(nonce)
    def initialize(self):
        self.name = 'BITFINEX'
        self.conn = httplib.HTTPSConnection("api.bitfinex.com")
        self.conn.request("GET","/v1/symbols")
        response = json.load(self.conn.getresponse())
        if response!=["btcusd","ltcusd","ltcbtc"]:
            self.lprint("! ERROR INITIALIZING BITFINEX - CURRENCIES DON'T MATCH UP"+'\n! '+response)
            raise Exception
    def balance(self):
        # Returns balance, which looks like {'BTC_EXCHANGE':0.82,'LTC_EXCHANGE':10.34}
        pass
    def trade(self, currency_from, currency_to, ratio, amount):
        # Executes trade corresponding to orderbook[currency_from][currency_to] = {'ratio':ratio,'volume':amount}
        # Blocks until trade is complete.
        pass
    def transfer(self, currency, amount, address):
        # Transfers currency (e.g, "BTC_EXCHANGE") in amount amount to external address address.
        pass
    def frame(self):
        self.conn.request("GET","/v1/book/ltcbtc")
        data = json.load(self.conn.getresponse())
        asks = data['asks']
        bids = data['bids']
        orderbook = {'LTC_BITFINEX':{'BTC_BITFINEX':[]},'BTC_BITFINEX':{'LTC_BITFINEX':[]}}
        for item in bids:
            orderbook['LTC_BITFINEX']['BTC_BITFINEX'].append({'cost':0.0,'ratio':float(item['price']),'volume':float(item['amount'])})
        for item in asks:
            orderbook['BTC_BITFINEX']['LTC_BITFINEX'].append({'cost':0.0,'ratio':1.0/float(item['price']),'volume':float(item['amount'])*float(item['price'])})
        return orderbook
    def balance(self):
        pass
    def cleanup(self):
        self.conn.close()

def testUpdate(valuable,unvaluable,orderbook):
#    print orderbook
    CUR_1 = valuable
    CUR_2 = unvaluable
#    print CUR_1,CUR_2,orderbook[CUR_1][CUR_2]
#    print CUR_2,CUR_1,orderbook[CUR_2][CUR_1]
    prices = [
              orderbook[CUR_2][CUR_1][0]['ratio'],
              1./orderbook[CUR_1][CUR_2][0]['ratio'],
              orderbook[CUR_1][CUR_2][0]['ratio'],
              1./orderbook[CUR_2][CUR_1][0]['ratio']
    ]
    if (prices == sorted(prices)):
        print 'seems to be working'
        print prices
        print sorted(prices)
    else:
        print 'does not seem to be working'
        print prices
        print sorted(prices)
    # should be the same
    time.sleep(10000)

plock = Lock()
bitce = BTCE(functools.partial(testUpdate,'BTC_BTCE','LTC_BTCE'),plock)
bitfinex = BITFINEX(functools.partial(testUpdate,'BTC_BITFINEX','LTC_BITFINEX'),plock)
#time.sleep(10)
#bitce.lprint(bitce.balance())

class MINTPAL(Exchange):

    def initialize(self):
        # Is called to initialize this module.
        # Recommend setting self.conn and all instance variables.
        self.name = 'MINTPAL'

        # conn = httplib.HTTPSConnection('api.mintpal.com')
        # conn.request('GET', '/v1/market/summary/btc')
        # data = json.load(conn.getresponse())
        # self.coins = [entry['code'] for entry in data]
        self.coins = ['LTC', 'DOGE']

    def balance(self):
        # Returns balance, which looks like {'BTC_EXCHANGE':0.82,'LTC_EXCHANGE':10.34}
        pass
    def trade(self, currency_from, currency_to, ratio, amount):
        # Executes trade corresponding to orderbook[currency_from][currency_to] = {'ratio':ratio,'volume':amount}
        # Blocks until trade is complete.
        pass
    def transfer(self, currency, amount, address):
        # Transfers currency (e.g, "BTC_EXCHANGE") in amount amount to external address address.
        pass

    def frame(self):
        # Is called very often and must return orderbook.
        # orderbook[CUR_1][CUR_2] = {'ratio': ratio, 'cost': cost, 'volume': volume}
        # If we start with volume of CUR_1, we can instantly turn it into (ratio*volume)-cost of CUR_2.
        # Conversion from cost in terms of CUR_1 before trade to cost in terms of CUR_2 after trade
        # (which is what we want) is cost_in_CUR_1_before_trade * ratio = cost_in_CUR_2_after_trade.

        orderbook = {'BTC_MINTPAL': {}}
        for coin in coins:
            # We need to populate the cost field correctly later
            conn = httplib.HTTPSConnection('api.mintpal.com')
            # This gives us buy orders for the coin in btc
            conn.request('GET', '/v1/market/orders/'+coin+'/btc/buy')
            buy_orders = json.load(conn.getresponse())
            highest_buy_order = buy_orders['orders'][0]
            orderbook[coin+'_MINTPAL'] = {}
            orderbook[coin+'_MINTPAL']['BTC_MINTPAL'] = {'ratio': float(highest_buy_order['price']), 'cost': 0.00, 'volume': float(highest_buy_order['amount'])}

            conn = httplib.HTTPSConnection('api.mintpal.com')
            # This gives orders for people selling <coin> for btc
            conn.request('GET', '/v1/market/orders/'+coin+'/btc/sell')
            sell_orders = json.load(conn.getresponse())
            lowest_sell_order = sell_orders['orders'][0]
            orderbook['BTC_MINTPAL'][coin+'_MINTPAL'] = {'ratio': float(lowest_sell_order['price']), 'cost': 0.00, 'volume': float(lowest_sell_order['amount'])}
        return orderbook

    def cleanup(self):
        # Called on exit. self.conn.close()?
        pass

class KRAKEN(Exchange):

    def initialize(self):
        # Is called to initialize this module.
        # Recommend setting self.conn and all instance variables.
        self.name = 'KRAKEN'
        self.coins = ['ltc', 'doge']
    def balance(self):
        # Returns balance, which looks like {'BTC_EXCHANGE':0.82,'LTC_EXCHANGE':10.34}
        pass
    def trade(self, currency_from, currency_to, ratio, amount):
        # Executes trade corresponding to orderbook[currency_from][currency_to] = {'ratio':ratio,'volume':amount}
        # Blocks until trade is complete.
        pass
    def transfer(self, currency, amount, address):
        # Transfers currency (e.g, "BTC_EXCHANGE") in amount amount to external address address.
        pass
    def frame(self):
        # Is called very often and must return orderbook.
        # orderbook[CUR_1][CUR_2] = {'ratio':ratio,'cost':cost,'volume':volume}
        # If we start with volume of CUR_1, we can instantly turn it into (ratio*volume)-cost of CUR_2.
        # Conversion from cost in terms of CUR_1 before trade to cost in terms of CUR_2 after trade
        # (which is what we want) is cost_in_CUR_1_before_trade * ratio = cost_in_CUR_2_after_trade.
        pass
    def cleanup(self):
        # Called on exit. self.conn.close()?
        pass

class BTER(Exchange):
    def initialize(self):
        # Is called to initialize this module.
        # Recommend setting self.conn and all instance variables.
        self.name = 'BTER'
        self.coins = ['ltc', 'doge']

    def balance(self):
        # Returns balance, which looks like {'BTC_EXCHANGE':0.82,'LTC_EXCHANGE':10.34}
        pass
    def trade(self, currency_from, currency_to, ratio, amount):
        # Executes trade corresponding to orderbook[currency_from][currency_to] = {'ratio':ratio,'volume':amount}
        # Blocks until trade is complete.
        pass
    def transfer(self, currency, amount, address):
        # Transfers currency (e.g, "BTC_EXCHANGE") in amount amount to external address address.
        pass
    def frame(self):
        # Is called very often and must return orderbook.
        # orderbook[CUR_1][CUR_2] = {'ratio':ratio,'cost':cost,'volume':volume}
        # If we start with volume of CUR_1, we can instantly turn it into (ratio*volume)-cost of CUR_2.
        # Conversion from cost in terms of CUR_1 before trade to cost in terms of CUR_2 after trade
        # (which is what we want) is cost_in_CUR_1_before_trade * ratio = cost_in_CUR_2_after_trade.
        orderbook = {'BTC_BTER': {}}
        for coin in self.coins:
            # We need to populate the cost field correctly later
            conn = httplib.HTTPSConnection('data.bter.com')
            # This gives us buy orders for the coin in btc
            conn.request('GET', '/api/1/ticker/'+coin+'_btc')
            response = json.load(conn.getresponse())
            orderbook['BTC_BTER'][coin.upper()+'_BTER'] = {'ratio': float(response['sell']), 'cost': 0.00, 'volume': float(response['vol_'+coin])}
            orderbook[coin.upper()+'_BTER'] = {}
            orderbook[coin.upper()+'_BTER']['BTC_BTER'] = {'ratio': float(response['buy']), 'cost': 0.00, 'volume': float(response['vol_btc'])}

            return orderbook

    def cleanup(self):
        # Called on exit. self.conn.close()?
        pass

class POLONIEX(Exchange):
    def initialize(self):
        # Is called to initialize this module.
        # Recommend setting self.conn and all instance variables.
        self.name = 'POLONIEX'
        self.conn = httplib.HTTPSConnection('poloniex.com')
        self.coins = ['LTC', 'DOGE']
    def balance(self):
        # Returns balance, which looks like {'BTC_EXCHANGE':0.82,'LTC_EXCHANGE':10.34}
        pass
    def trade(self, currency_from, currency_to, ratio, amount):
        # Executes trade corresponding to orderbook[currency_from][currency_to] = {'ratio':ratio,'volume':amount}
        # Blocks until trade is complete.
        pass
    def transfer(self, currency, amount, address):
        # Transfers currency (e.g, "BTC_EXCHANGE") in amount amount to external address address.
        pass
    def frame(self):
        # Is called very often and must return orderbook.
        # orderbook[CUR_1][CUR_2] = {'ratio':ratio,'cost':cost,'volume':volume}
        # If we start with volume of CUR_1, we can instantly turn it into (ratio*volume)-cost of CUR_2.
        # Conversion from cost in terms of CUR_1 before trade to cost in terms of CUR_2 after trade
        # (which is what we want) is cost_in_CUR_1_before_trade * ratio = cost_in_CUR_2_after_trade.
        orderbook = {'BTC_POLONIEX'}
        for coin in self.coins:
            params = {'command': 'returnOrderBook', 'currencyPair': 'BTC_'+coin}
            self.conn.request('GET', '/public')
            data = json.load(self.conn.getresponse())
            orderbook['BTC_POLONIEX'][coin+'_POLONIEX'] = {'ratio': data['asks'][0][0], 'cost': 0.00, 'volume': data['asks'][0][1]}
            orderbook[coin+'_POLONIEX'] = {}
            orderbook[coin+'_POLONIEX']['BTC_POLONIEX'] = {'ratio': data['bids'][0][0], 'cost': 0.00, 'volume': bids['asks'][0][1]}
        return orderbook
    def cleanup(self):
        # Called on exit. self.conn.close()?
        pass

class CRYPTSY(Exchange):
    def initialize(self):
        # Is called to initialize this module.
        # Recommend setting self.conn and all instance variables.
        self.name = 'CRYPTSY'
    def balance(self):
        # Returns balance, which looks like {'BTC_EXCHANGE':0.82,'LTC_EXCHANGE':10.34}
        pass
    def trade(self, currency_from, currency_to, ratio, amount):
        # Executes trade corresponding to orderbook[currency_from][currency_to] = {'ratio':ratio,'volume':amount}
        # Blocks until trade is complete.
        pass
    def transfer(self, currency, amount, address):
        # Transfers currency (e.g, "BTC_EXCHANGE") in amount amount to external address address.
        pass
    def frame(self):
        # Is called very often and must return orderbook.
        # orderbook[CUR_1][CUR_2] = {'ratio':ratio,'cost':cost,'volume':volume}
        # If we start with volume of CUR_1, we can instantly turn it into (ratio*volume)-cost of CUR_2.
        # Conversion from cost in terms of CUR_1 before trade to cost in terms of CUR_2 after trade
        # (which is what we want) is cost_in_CUR_1_before_trade * ratio = cost_in_CUR_2_after_trade.
        pass
    def cleanup(self):
        # Called on exit. self.conn.close()?
        pass

class EXMONEY(Exchange):
    def initialize(self):
        # Is called to initialize this module.
        # Recommend setting self.conn and all instance variables.
        self.name = 'EXMONEY'
    def balance(self):
        # Returns balance, which looks like {'BTC_EXCHANGE':0.82,'LTC_EXCHANGE':10.34}
        pass
    def trade(self, currency_from, currency_to, ratio, amount):
        # Executes trade corresponding to orderbook[currency_from][currency_to] = {'ratio':ratio,'volume':amount}
        # Blocks until trade is complete.
        pass
    def transfer(self, currency, amount, address):
        # Transfers currency (e.g, "BTC_EXCHANGE") in amount amount to external address address.
        pass
    def frame(self):
        # Is called very often and must return orderbook.
        # orderbook[CUR_1][CUR_2] = {'ratio':ratio,'cost':cost,'volume':volume}
        # If we start with volume of CUR_1, we can instantly turn it into (ratio*volume)-cost of CUR_2.
        # Conversion from cost in terms of CUR_1 before trade to cost in terms of CUR_2 after trade
        # (which is what we want) is cost_in_CUR_1_before_trade * ratio = cost_in_CUR_2_after_trade.
        pass
    def cleanup(self):
        # Called on exit. self.conn.close()?
        pass

