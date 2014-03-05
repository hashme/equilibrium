import urllib
import urllib2, time

def execute(CUR_FROM, CUR_TO, volume, price):
    url = 'https://poloniex.com/tradingApi'
    alt_currency = ''
    if CUR_FROM=='BTC':
        alt_currency = CUR_TO
        rate = str(1.0/float(price))
        command = 'buy'
    if CUR_TO=='BTC':
        alt_currency = CUR_FROM
        rate = str(price)
        command = 'sell'
    values = {
'Key':'YGPVHQFC-S2E7Y80I-QNPOFXCY-VT0C4PQS',
'Sign':'d0c648e66ff9dce29f007c3876c659553336d438f2cf5d700be7d5959053141200c2e5ea0250bdabdd0e865b1cd5a723b1eb2c496be41cdab417a6b7b3055f5d',
'amount':str(volume),
'rate':rate,
'command':command,
'currencyPair':'BTC_'+alt_currency
             }
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req).read()
    print response
    time.sleep(0.5)
    while True:
        url = 'https://poloniex.com/tradingApi'
        values = {
'Key':'YGPVHQFC-S2E7Y80I-QNPOFXCY-VT0C4PQS',
'Sign':'d0c648e66ff9dce29f007c3876c659553336d438f2cf5d700be7d5959053141200c2e5ea0250bdabdd0e865b1cd5a723b1eb2c496be41cdab417a6b7b3055f5d',
'command':'returnOpenOrders',
'currencyPair':'BTC_'+alt_currency
                 }
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req).read()
        print response
        if response=="[]":break


execute('BTC','DOGE',10,0.00000175)
