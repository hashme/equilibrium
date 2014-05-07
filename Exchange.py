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
    def lprint(self,text):
        with self.printlock:
            print text
    def initialize(self):
        pass
    def frame(self):
        pass
    def cleanup(self):
        pass
    def balance(self):
        pass
    def trade(self, currency_from, currency_to, amount, price):
        # This is just executing the trade orderbook[currency_from][currency_to] = {volume:amount}
        pass
    def transfer(self, currency, amount, address):
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
            # Fees aren't being taken into account - eventually they should be
            for variable_cost,volume in asks:
                orderbook[CUR_1][CUR_2].append({'fixed_cost':0.0,'variable_cost':variable_cost,'volume':volume})
            orderbook[CUR_2][CUR_1] = []
            for variable_cost,volume in bids:
                orderbook[CUR_2][CUR_1].append({'fixed_cost':0.0,'variable_cost':1.0/variable_cost,'volume':volume})
        return orderbook
    def cleanup(self):
        self.conn.close()

def testUpdate(valuable,unvaluable,orderbook):
    CUR_1 = valuable
    CUR_2 = unvaluable
    prices = [
              1./orderbook[CUR_1][CUR_2][0]['variable_cost'],
              orderbook[CUR_2][CUR_1][0]['variable_cost'],
              1./orderbook[CUR_2][CUR_1][0]['variable_cost'],
              orderbook[CUR_1][CUR_2][0]['variable_cost']
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

bitce = BTCE(functools.partial(testUpdate,'BTC_BTCE','LTC_BTCE'),Lock())
time.sleep(10)
bitce.lprint(bitce.balance())

class BITFINEX(ExchangeData):
    def initialize(self):
        self.name = 'BITFINEX'
        self.conn = httplib.HTTPSConnection("api.bitfinex.com")
        self.conn.request("GET","/v1/symbols")
        response = self.conn.getresponse()
        if response!='["btcusd","ltcusd","ltcbtc"]':
            self.lprint("! ERROR INITIALIZING BITFINEX - CURRENCIES DON'T MATCH UP"+'\n! '+response)
            raise Exception
    def frame(self):
        self.conn.request("GET","/v1/book/ltcbtc")
        data = json.load(self.conn.getresponse())
        asks = data['asks']
        bids = data['bids']
        orderbook = {'LTC_BITFINEX':{'BTC_BITFINEX':[]},'BTC_BITFINEX':{'LTC_BITFINEX':[]}}
        for item in asks:
            orderbook['LTC_BITFINEX']['BTC_BITFINEX'].append({'fixed_cost':0.0,'variable_cost':,'volume':})
        for item in bids:
            orderbook['BTC_BITFINEX']['LTC_BITFINEX'].append({'fixed_cost':0.0,'variable_cost':,'volume':})


            for variable_cost,volume in asks:
                orderbook[CUR_1][CUR_2].append({'fixed_cost':0.0,'variable_cost':variable_cost,'volume':volume})
            orderbook[CUR_2][CUR_1] = []
            for variable_cost,volume in bids:
                orderbook[CUR_2][CUR_1].append({'fixed_cost':0.0,'variable_cost':1.0/variable_cost,'volume':volume})
        
    def balance(self):
        pass
    def cleanup(self):
        self.conn.close()

class MINTPAL(ExchangeData):
    def initialize(self):
        self.name = 'MINTPAL'
    def frame(self):
        pass
    def cleanup(self):
        pass

class KRAKEN(ExchangeData):
    def initialize(self):
        self.name = 'KRAKEN'
    def frame(self):
        pass
    def cleanup(self):
        pass

class BTER(ExchangeData):
    def initialize(self):
        self.name = 'BTER'
    def frame(self):
        pass
    def cleanup(self):
        pass

class POLONIEX(ExchangeData):
    def initialize(self):
        self.name = 'POLONIEX'
    def frame(self):
        pass
    def cleanup(self):
        pass

class EXMONEY(ExchangeData):
    def initialize(self):
        self.name = 'EXMONEY'
    def frame(self):
        pass
    def cleanup(self):
        pass
