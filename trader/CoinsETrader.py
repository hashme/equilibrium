import CoinsE
def execute(CUR_FROM, CUR_TO, volume, price): # all need to be strings
    volume = str(volume)
    price = str(volume)
    working_pair1 = CUR_FROM+'_'+CUR_TO #sell
    working_pair2 = CUR_TO+'_'+CUR_FROM #buy
    amount = Coinse.authenticated_request('wallet/%s/' % (CUR_FROM), 'getwallets')
    if float(volume) > float(amount['available']):
        volume = str(amount['available'])

    b = Coinse.authenticated_request('market/%s/' % (working_pair1),"neworder",{'order_type':'sell',
                                                                                         'rate':price,
                                                                                         'quantity':volume,})
    if b['status']:
        Coinse.authenticated_request('market/%s/' % (working_pair2),"neworder",{'order_type':'buy',
                                                                                         'rate':price,
                                                                                         'quantity':volume,})
