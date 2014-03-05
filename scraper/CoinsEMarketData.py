__author__ = 'Smith'
import urllib
import json

class CoinsEMarketData:
    def __init__(self):
        self.withdrawal_fees = {}
        self.fee_dict={}


    def getMarketPrices(self):
        arc_dict = self.withdrawal_fees
        coinListUrl = 'https://www.coins-e.com/api/v2/markets/data/'
        response = urllib.urlopen(coinListUrl)
        jsonResponse = response.read().decode("utf-8")
        decoded = json.loads(jsonResponse)

        for market in decoded['markets']:
            ##add coin one node and exchange arc to dictionary
            if(decoded['markets'][market]['status']=='healthy'):
                if(len(decoded['markets'][market]['marketdepth']['asks'])>0):

                    currency2node = {decoded['markets'][market]['c2'] + "_coins-e": [(1-self.fee_dict.get(decoded['markets'][market]['c1']))/float(decoded['markets'][market]['marketdepth']['asks'][0]['r']),float(decoded['markets'][market]['marketdepth']['asks'][0]['cq'])]}
                    str = decoded['markets'][market]['c1'] + '_coins-e'
                    if(str in arc_dict.keys()):
                        arc_dict.get(decoded['markets'][market]['c1'] + "_coins-e").update(currency2node)
                    else:
                        arc_dict.update({decoded['markets'][market]['c1'] + "_coins-e":currency2node})

                if(len(decoded['markets'][market]['marketdepth']['bids'])>0):
                    ##add coin 2 node and arc to dictionary
                    currency2node = {decoded['markets'][market]['c1'] + "_coins-e":[(1-self.fee_dict.get(decoded['markets'][market]['c1']))*float(decoded['markets'][market]['marketdepth']['bids'][0]['r']),float(decoded['markets'][market]['marketdepth']['bids'][0]['cq'])*float(decoded['markets'][market]['marketdepth']['bids'][0]['r'])]}
                    if((decoded['markets'][market]['c2'] + '_coins-e') in arc_dict.keys()):
                        arc_dict.get(decoded['markets'][market]['c2'] + "_coins-e").update(currency2node)
                    else:
                        arc_dict.update({decoded['markets'][market]['c2'] + "_coins-e":currency2node})

        return arc_dict

    def calcTransactionFees(self):
        self.withdrawal_fees = {}
        self.fee_dict = {}
        coinListUrl = 'https://www.coins-e.com/api/v2/coins/list/'
        response = urllib.urlopen(coinListUrl)
        jsonResponse = response.read().decode("utf-8")
        decoded = json.loads(jsonResponse)

        for coin in decoded['coins']:
            self.fee_dict.update({coin['coin']:float(coin['trade_fee'])})
            self.withdrawal_fees.update({coin['coin']+"_coins-e":{coin['coin']:float(coin['withdrawal_fee'])}})


def getMarketPrices():
    marketinstance = CoinsEMarketData()
    marketinstance.calcTransactionFees()
    return marketinstance.getMarketPrices()


