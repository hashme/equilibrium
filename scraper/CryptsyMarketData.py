__author__ = 'Smith'
__author__ = 'Smith'

import urllib
import json

class CryptsyMarketData:
    def __init__(self):
        self.witdrawal_fees={}

    def getMarketPrices(self):
        arc_dict = {}
        coinListUrl = 'http://pubapi.cryptsy.com/api.php?method=marketdatav2'
        response = urllib.urlopen(coinListUrl)
        jsonResponse = response.read().decode("utf-8")
        decoded = json.loads(jsonResponse)

        for market in decoded['return']['markets']:
            ##add coin one node and exchange arc to dictionary

            currency2node = {decoded['return']['markets'][market]['secondarycode'] + "_cryptsy":[.998/float(decoded['return']['markets'][market]['sellorders'][0]['price']),float(decoded['return']['markets'][market]['sellorders'][0]['quantity'])]}
            str = decoded['return']['markets'][market]['primarycode'] + '_cryptsy'
            if(str in arc_dict.keys()):
                arc_dict.get(decoded['return']['markets'][market]['primarycode'] + "_cryptsy").update(currency2node)
            else:
                arc_dict.update({decoded['return']['markets'][market]['primarycode'] + "_cryptsy":currency2node})

            ##add coin 2 node and arc to dictionary
            currency2node = {decoded['return']['markets'][market]['primarycode'] + "_cryptsy":[.997*float(decoded['return']['markets'][market]['buyorders'][0]['price']),float(decoded['return']['markets'][market]['buyorders'][0]['quantity'])*float(decoded['return']['markets'][market]['buyorders'][0]['price'])]}

            if((decoded['return']['markets'][market]['secondarycode'] + '_cryptsy') in arc_dict.keys()):
                arc_dict.get(decoded['return']['markets'][market]['secondarycode'] + "_cryptsy").update(currency2node)
            else:
                arc_dict.update({decoded['return']['markets'][market]['secondarycode'] + "_cryptsy":currency2node})

        return arc_dict

    def getWithdrawalFees(self):
        arc_dict ={}

def getMarketPrices():
    market = CryptsyMarketData()
    return market.getMarketPrices()
    ##print prices['BTC_cryptsy']['DRK_cryptsy']
    ##print prices['DRK_cryptsy']












