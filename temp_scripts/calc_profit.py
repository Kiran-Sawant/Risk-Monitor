import MetaTrader5 as mt5
import datetime as dt
import time

mt5.initialize()

position = mt5.positions_get(symbol='USDTRY')
# print(position)

def profit(position):

    if position[0].type == 0:              #For long positions
        type_ = mt5.ORDER_TYPE_BUY
    else:
        type_ = mt5.ORDER_TYPE_SELL

    profit = mt5.order_calc_profit(type_, position[0].symbol, position[0].volume, position[0].price_open, position[0].sl)
    return profit

k = profit(position)
print(k)

mt5.shutdown()