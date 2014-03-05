__author__ = 'Smith'
import urllib
import json
import operator
from ..API.bterapi import bterconnection
from ..API.bterapi import common
import threading

pair_list=[]
fee_dict= {}


def getMarketData( pair, arc_dict):
        ##arc_dict = self.withdrawal_fees
        connection = bterconnection.BTERConnection()
        try:
            depth = common.validateResponse(connection.makeJSONRequest('/api/1/depth/%s' % pair, method='GET'))
            coins = pair.upper().split("_")
            if len(depth['asks']) > 0:
                asks = sorted(depth['asks'], key=lambda x: float(x[0]))
                currency2node = {coins[1] + "_bter": [(.998)/float(asks[0][0]), float(asks[0][1])]}
                str = coins[0] + '_bter'
                if(str in arc_dict.keys()):
                    arc_dict.get(coins[0] + "_bter").update(currency2node)
                else:
                    arc_dict.update({coins[0] + "_bter":currency2node})
                if(len(depth['bids'])>0):
                    bids = sorted(depth['bids'], key=lambda x: -1.0*(float(x[0])))
                     ##add coin 2 node and arc to dictionary
                    currency2node = {coins[0] + "_bter":[(.998)*float(bids[0][0]),float(bids[0][1])*float(bids[0][0])]}
                if((coins[1] + '_bter') in arc_dict.keys()):
                    arc_dict.get(coins[1] + "_bter").update(currency2node)
                else:
                    arc_dict.update({coins[1] + "_bter":currency2node})
        except:
            raise





def getTickerList():
    try:
        return bterconnection.BTERConnection().makeJSONRequest("/api/1/pairs", method="GET")
    except:
        print 'wtf'



def getMarketPrices():
    arc_dict={}
    pair_list =getTickerList()
    threads =[]
    results=[]

    from multiprocessing.pool import ThreadPool

    pool = ThreadPool(processes=4)
    for pair in pair_list:
        results.append(pool.apply_async(getMarketData, (pair, arc_dict)))
    for return_val in results:
        return_val.get()
    if "LTC_bter" in arc_dict:
        if "LTC_bter" in arc_dict['LTC_bter']:
            del arc_dict["LTC_bter"]["LTC_bter"]


    return arc_dict












