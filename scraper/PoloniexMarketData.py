import urllib, urllib2, time

def getMarketPrices():
    currency_pairs = ['BTC_FOX', 'BTC_FLAP', 'BTC_WIKI', 'BTC_CNOTE', 'BTC_CORG', 'BTC_MINT', 'BTC_AUR', 'BTC_REDD', 'BTC_UTC', 'BTC_MEC', 'BTC_DOGE', 'LTC_MEC', 'BTC_MAX', 'BTC_XCP', 'BTC_MMC', 'LTC_PAND', 'BTC_BC', 'LTC_MRC', 'BTC_FZ', 'BTC_MTS', 'BTC_DRK', 'LTC_IFC', 'BTC_PRC', 'BTC_SOC', 'BTC_GRC', 'LTC_EAC', 'LTC_SUN', 'BTC_PMC', 'BTC_WOLF', 'BTC_RIC', 'LTC_LEAF', 'BTC_ICN', 'BTC_XPM', 'BTC_NOBL', 'BTC_NXT', 'BTC_VTC', 'BTC_USDE', 'BTC_CACH', 'BTC_LTC', 'BTC_FRQ', 'BTC_NMC', 'BTC_eTOK', 'BTC_IXC', 'BTC_Q2C', 'BTC_GLB', 'LTC_NXT', 'BTC_SMC', 'BTC_CON', 'BTC_CASH', 'BTC_HUC', 'BTC_MEOW', 'BTC_SXC', 'LTC_DIME', 'BTC_KDC', 'BTC_CGA', 'BTC_MYR', 'BTC_PTS', 'BTC_OLY']
    data = {}
    data['BTC_poloniex'] = {}
    for currency_pair in filter(lambda x:'BTC_' in x,currency_pairs):
        now = time.time()
        order_book = eval(urllib.urlopen('http://poloniex.com/public?command=returnOrderBook&currencyPair='+currency_pair).read())
        currency = currency_pair.split('_')[1]
        try:
            asks = order_book['asks'][0]
            bids = order_book['bids'][0]
            btc_primary = bids
            other_primary = [1./asks[0], asks[1]]
            data['BTC_poloniex'][currency+'_poloniex'] = btc_primary
            data[currency+'_poloniex'] = {'BTC_poloniex':other_primary}
            time.sleep(max([0,0.1-(time.time()-now)]))
        except:
            time.sleep(max([0,0.1-(time.time()-now)]))
    return data


