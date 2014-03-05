import Cryptsy

def execute(CUR_FROM, CUR_TO, volume, price):
    volume = str(volume)
    price = str(price)
    Exchange = Cryptsy.Cryptsy('27c9ac057d3a1c4c0f1eb5bc03f3cfdaa1abbeb4','c3d554d06b9d09f9b8e1ef8432de96051ab16b48399b25aa257d404913cce4d44fa82b1fffa1e883')
    data = Exchange.getMarkets()
    data2 = Exchange.getInfo()
    data2 = float(data2['return']['balances_available'][CUR_FROM])
    if float(data2) < float(volume):
        volume = str(data2)
    ref1 = filter(lambda x:x['primary_currency_code']==CUR_FROM and x['secondary_currency_code']==CUR_TO, data['return'])
    if ref1:
        MID = ref1[0]['marketid']
        whatdo = "Sell"
        Exchange.createOrder(MID, whatdo, volume, price)
    else:
        ref2 = filter(lambda x:x['primary_currency_code']==CUR_TO and x['secondary_currency_code']==CUR_FROM, data['return'])
        if ref2:
            MID = ref2[0]['marketid']
            whatdo = "Buy"
            Exchange.createOrder(MID, whatdo, volume, price)

