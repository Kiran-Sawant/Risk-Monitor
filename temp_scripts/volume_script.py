import MetaTrader5 as mt5

mt5.initialize()

forex = ['EUR', 'GBP', 'AUD', 'NZD', 'USD', 'CHF', 'CAD', 'SGD', 'NOK', 'SEK']

commodity = ['XAU', 'XPD', 'XPT', 'XNG', 'XTI', 'XBR', 'DXY']

positions = mt5.positions_get(symbol='AUDJPY')
# print(positions)

def volAdjust(vol, asset):
    
    if asset[0:3] in forex:
        return vol * 100000
    elif asset[0:3] in commodity:
        return vol * 100
    elif asset[0:3] == 'XAG':
        return vol * 1000
    else:
        return vol

def volume(positions):

    if len(positions) == 1:         #For one trade/asset
        if positions[0].type == 0:
            lot = positions[0].volume
        else:
            lot = -(positions[0].volume)
        return volAdjust(lot, positions[0].symbol)
    else:                           #For more than one trades 
        volume_ = 0
        for i in positions:
            if i.type == 0:         #for a long position
                volume_ += i.volume
            else:                   #For a short position
                volume_ -= i.volume
        return volAdjust(volume_, positions[0].symbol)

def exposure(positions):

    exposure_ = 0
    if len(positions) == 1:
        exposure_ = volume(positions) * positions[0].price_open
        return exposure_
    else:
        exposure_ = 0
        for i in positions:
            if i.type == 0:
                exposure_ += volAdjust(i.volume, i.symbol) * i.price_open
            else:
                exposure_ -= volAdjust(i.volume, i.symbol) * i.price_open
            return exposure_

print(f"Volumes: {volume(positions)}")
print(f"Exposure: {exposure(positions)}")

mt5.shutdown()