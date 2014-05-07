import urllib
import urllib2
import httplib
import hashlib
import hmac
import time
import json
from multiprocessing import Process, Lock

class ExchangeData:
    def lprint(self,text):
        with self.printlock:
            print text
    def initialize(self):
        pass
    def frame(self):
        pass
    def cleanup(self):
        pass
    def run(self):
        self.initialize()
        while True:
            try:
                self.callback(self.frame())
            except KeyboardInterrupt:
                self.lprint('! CAUGHT KEYBOARD INTERRUPT')
                break
            except Exception as e:
                self.lprint('! ERROR GRABBING DATA IN EXCHANGE {0}'.format(self.name))
                self.lprint('! ' + str(e))
        self.cleanup()
    def balance(self):
        pass
    def __init__(self, callback, printlock):
        self.callback = callback
        self.printlock = printlock
        p = Process(target = self.run)
        p.start()

class BTCE(ExchangeData):
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
        print nonce
        return str(nonce)
    def initialize(self):
        self.name = 'BTCE'
        self.BTC_api_key = "E7UP1XGZ-YVSGL06A-1IIMJBLC-EQFQT2JV-DY4QED4H"
        self.BTC_api_secret = "59445bb18d7a33cc40f803a2a72f7ac2e687ccd11ddbd8e5843be56b30eb5755"
        self.forbidden_currencies = ['USD','CNC']
        self.conn = httplib.HTTPSConnection("btc-e.com")
        self.conn.request("GET","/api/3/info")
        response = json.load(self.conn.getresponse())
        self.fees = dict(map(lambda i: (i[0],float(i[1]['fee'])/100.),response['pairs'].items()))
        self.pairs = filter(lambda x:x not in self.forbidden_currencies,self.fees.keys())
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
        orderbook = {}
        self.conn.request("GET","/api/3/depth/"+'-'.join(self.pairs))
        response = json.load(self.conn.getresponse())
        for pair,data in response.keys():
            CUR_1,CUR_2 = map(lambda x:x.upper(),pair.split("_"))
            asks = data['asks']
            bids = data['bids']
            orderbook[CUR_1][CUR_2] = []
            for variable_cost,volume in asks:
                orderbook[CUR_1][CUR_2].append({'fixed_cost':0.0,'variable_cost':variable_cost,'volume':volume})
            orderbook[CUR_2][CUR_1] = []
            for variable_cost,volume in bids:
                orderbook[CUR_2][CUR_1].append('fixed_cost':0.0,'variable_cost':1.0/variable_cost,'volume':volume})
        return orderbook
    def cleanup(self):
        self.conn.close()

def loprint(text):print text
bitce = BTCE(loprint,Lock())

class BITFINEX(ExchangeData):
    def initialize(self):
        self.name = 'BITFINEX'
    def frame(self):
        pass
    def cleanup(self):
        pass

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

