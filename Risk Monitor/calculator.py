"""This module calculates or returns various parameters of an MT5 account, an open trade and a pending order
    that are crucial for a trader to know and constantly monitor.
    This module consists of three classes for creating account, position and order objects.
    This module uses MetaTrader5 module to retrive data and works only with MetaTrader5"""

#_________Imports________#
import datetime as dt
import time

import MetaTrader5 as mt5

print(f"Author: {mt5.__author__}")
print(f"Module Version: {mt5.__version__}")

#_________________Creating Data structures_________________#
"""Forex & Commodity list is required by real_volume() method
    list1 consists of asset names & their Dollar conversion
    required to calculat P/L."""

forex = ['EUR', 'GBP', 'AUD', 'NZD', 'USD', 'CHF', 'CAD', 'SGD', 'NOK', 'SEK',]                             #Required to calculate volume

commodity = ['XAU', 'XPD', 'XPT', 'XNG', 'XTI', 'XBR', 'DXY', 'JGB']                                        #Required to calculate volume

# list1 = {'GBPAUD': 'AUDUSD', 'EURAUD': 'AUDUSD', 'AUDNZD': 'NZDUSD', 'GBPNZD': 'NZDUSD', 'EURNZD': 'NZDUSD',
#         'EURGBP': 'GBPUSD', 'GBPCHF': 'USDCHF', 'EURCHF': 'USDCHF', 'AUDCHF': 'USDCHF', 'CADCHF': 'USDCHF',
#         'NZDCHF': 'USDCHF', 'GBPJPY': 'USDJPY', 'CHFJPY': 'USDJPY', 'EURJPY': 'USDJPY', 'AUDJPY': 'USDJPY',
#         'CADJPY': 'USDJPY', 'NZDJPY': 'USDJPY', 'SGDJPY': 'USDJPY', 'NOKJPY': 'USDJPY', 'SEKJPY': 'USDJPY',
#         'GBPCAD': 'USDCAD', 'EURCAD': 'USDCAD', 'AUDCAD': 'USDCAD', 'NZDCAD': 'USDCAD', 'GBPSGD': 'USDSGD',
#         'CHFSGD': 'USDSGD', 'EURSGD': 'USDSGD', 'AUDSGD': 'USDSGD', 'GBPNOK': 'USDNOK', 'EURNOK': 'USDNOK',
#         'GBPSEK': 'USDSEK', 'EURSEK': 'USDSEK', 'NOKSEK': 'USDSEK', 'GBPTRY': 'USDTRY', 'EURTRY': 'USDTRY',
#         'EURZAR': 'USDZAR', 'GBPDKK': 'USDDKK', 'EURDKK': 'USDDKK', 'EURHKD': 'USDHKD', 'EURPLN': 'USDPLN',
#         'XAUEUR': 'EURUSD', 'XAUAUD': 'AUDUSD', 'XAGEUR': 'EURUSD', 'AUS200': 'AUDUSD', 'UK100': 'GBPUSD',
#         'JP225': 'USDJPY', 'DE30': 'EURUSD', 'STOXX50': 'EURUSD', 'F40': 'EURUSD', 'ES35': 'EURUSD',
#         'IT50': 'EURUSD', 'HK50': 'USDHKD'}

mt5.initialize()             #Connecting to MT5
print(f"Terminal Build: {mt5.terminal_info().build}\n")

#__________________Creating Denomination Dictionary_____________________#
def pair_generator(symbol):         # symbol: Profit currency.
    """Takes the currency symbol and returns the USD converting forex pair,
        ie. for AUD it will return AUDUSD & USDJPY for JPY, etc."""

    if symbol in ['EUR', 'GBP', 'AUD', 'NZD']:
        return f'{symbol}USD'
    else:
        return f'USD{symbol}'

#_______________creating list1(line-24) automatically__________________#
allinfo = mt5.symbols_get()

templist = list()
for info in allinfo:
    if info.currency_profit == 'USD' or info.currency_margin == 'USD':
        continue
    else:
        templist.append((info.name, info.currency_profit))

list1 = dict()
for i in templist:
    list1[i[0]] = pair_generator(i[1])

#______________________Account class______________________#
class Account():
    """Gives real-time details of the account that is currently logged in the MT5 terminal"""

    def __init__(self):
        self.info = mt5.account_info()                          #Info tuple

        self.name = self.info.name                              #Account holders name
        self.server = self.info.server                          #Server name
        self.profit = self.info.profit                          #Current P/L
        self.balance = self.info.balance                        #money before taking any position
        self.equity = self.info.equity                          #balance +- Profit/Loss
        self.margin = self.info.margin                          #Collatral paid to the broker
        self.free_margin = self.info.margin_free                #Usable amount
        self.margin_level = f"{self.info.margin_level:.2f}%"    #paid margin as a percentage of equity


    def mode(self):
        """Returns mode in which the account is active.
        Demo or Live"""

        if self.info.trade_mode == 0:
            return 'Demo'
        else:
            return 'Live!'

#______________________Position class______________________#
class Position():
    """Returns or calculates various parmeters of an asset that has a single or multiple open positions.
    
    Argument:
        symbol: The symbol of a current open position"""

    def __init__(self, symbol: str):

        self.open_positions = mt5.positions_get(symbol=symbol)      #Info tuple of open tuples

        self.asset = symbol                                         #Symbol of asset
        self.current_price = self.open_positions[0].price_current   #Current price of the asset
        self.trades = len(self.open_positions)                      #Number of open trades on this asset
    
    @staticmethod
    def _fxAdjust(exposure, pair):
        """Converts the passed exposure in USD
        
        Attr:
            exposure: amount that is needed to be converted into USD.
            pair: currency pair that converts the exposures denomination into USD"""
        
        if pair[0:3] == 'USD':
            adjustedExpo = exposure / mt5.symbol_info_tick(pair).ask
        else:
            adjustedExpo = exposure * mt5.symbol_info_tick(pair).ask

        return adjustedExpo
    
    @staticmethod
    def _volAdjust(vol, asset):
        """Converts MT5 volume format into real volume"""
    
        if asset[0:3] in forex:
            return vol * 100000
        elif asset[0:3] in commodity:
            return vol * 100
        elif asset[0:3] == 'XAG':
            return vol * 1000
        else:
            return vol

    def position(self):
        """Returns net position on an asset; Net Long or Net Short."""

        string = ''
        if self.trades == 1:                       #For 1 trade/asset
            type_ = self.open_positions[0].type
            if type_ == 0:
                string = 'Net Long'
            else:
                string = 'Net Short'
            return string
        else:                                      #For > one trade/asset
            if self.real_volume() > 0:
                return "Net long"
            elif self.real_volume() < 0:
                return "Net Short"
            else:
                return 'Heged'

    def entry_price(self):
        """Gives the cumulative entry price for all the positions of an asset."""

        if self.trades == 1:                    #For 1 trade/asset
            entry = self.open_positions[0].price_open
            return entry
        else:                                   #For > 1 trade/asset
            if self.real_volume() == 0:         #For Heged trades
                sum_ = 0
                for i in self.open_positions:
                    sum_ += i.price_open
                entry = sum_ / self.trades      #for heged trade, I considered arithmetic mean of entry_prices as entry
                return entry
            else:
                entry = self.real_exposure() / self.real_volume()
                return entry
      
    def raw_volume(self, named_tupl):
        """raw_volume() does the same thing as real_volume().
        unlike real_volume() it takes a named tuple only."""

        if named_tupl.type == 0:                #For long positions
            return self._volAdjust(named_tupl.volume, named_tupl.symbol)
        else:
            return -(self._volAdjust(named_tupl.volume, named_tupl.symbol))

    def real_volume(self):
        """Calculates the cumulative volume on an asset. Adjusting for long/short positions
        Addition for Long Positions & Negation for short position."""

        if self.trades == 1:                #For one trade/asset
            volume_ = self.open_positions[0].volume
            return self._volAdjust(volume_, self.asset)
        else:                               #For > one trade/asset
            volume_ = 0
            for i in self.open_positions:
                if i.type == 0:             #For a long position
                    volume_ += i.volume
                else:                       #For a short position
                    volume_ -= i.volume
            return self._volAdjust(volume_, self.asset)

    def real_exposure(self):
        '''Gives the exposure of asset without forex adjusting
           ie: exposure denominated in margin currency.'''

        if self.trades == 1:                                    #if one trade/asset
            rExposure = self.real_volume() * self.entry_price()
            return rExposure
        else:                                                   #if > one trade/asset
            rExposure = 0
            for i in self.open_positions:
                rExposure += self.raw_volume(i) * i.price_open
            return rExposure

    def adjusted_exposure(self):
        """Gives the exposure denominated in USD.
           note: the forex rate is current & not 
           from the time @ which trade was executed"""

        if self.asset[0:3] == 'USD':                                    #Asset with USD base
            return self.real_volume()

        elif self.asset in list1:                                       #A non-dollar denominated asset
            fx_expo = self._fxAdjust(self.real_exposure(), list1[self.asset])
            return fx_expo

        else:                                                           #Dollar denominated asset
            return self.real_exposure()

    def leverage(self, account: Account) -> None:
        """Returns Leverage of position against account equity. Requires an Account object"""

        lev = self.adjusted_exposure() / account.equity
        return abs(lev)
            
    def appriciation(self):
        """Returns appriciation/depriciation of asset from entry.
        w.r.t the position ie. Long/Short."""

        appr = (self.current_price - self.entry_price())/self.entry_price()
        
        if self.position() == 'Net Long':          # appriciation on long positions  

            return appr
            
        elif self.position() == 'Net Short':       # appriciation on short positions
            if appr < 0:
                return abs(appr)
            else:
                return -(appr)
        else:                                      # appriciation on hedged position
            return 0
    
    def status(self):
        """"Returns a string indicating the overall status of position; Profitable or Losing."""

        if self.profit() > 0:
            return "Profitable"
        elif self.profit() < 0:
            return "Losing"
        else:
            return "Null"

    def capital_risk(self, account: Account):
        """Returns the $ amount that will be lost if SL is filled.
        If no SL is placed it returns account equity as entire equity is @ risk.
        Requires an account object for equity"""

        if self.trades == 1:                                #For one trades/asset
            if self.open_positions[0].type == 0:            #For long positions
                type_ = mt5.ORDER_TYPE_BUY
            else:
                type_ = mt5.ORDER_TYPE_SELL
            
            # try:
            #     risk = mt5.order_calc_profit(type_, self.asset, self.open_positions[0].volume, self.open_positions[0].price_open, self.open_positions[0].sl)
            # except TypeError:
            #     risk = account.equity
            risk = mt5.order_calc_profit(type_, self.asset, self.open_positions[0].volume, self.open_positions[0].price_open, self.open_positions[0].sl)
            if risk == None:
                return -(account.equity)
            else:
                return risk

        else:                                               #For > one trades/asset
            risk = 0
            for i in self.open_positions:
                if i.type == 0:
                    orderType = mt5.ORDER_TYPE_BUY
                else:
                    orderType = mt5.ORDER_TYPE_SELL
                try:
                    risk += mt5.order_calc_profit(orderType, self.asset, i.volume, i.price_open, i.sl)
                except TypeError:
                    risk = -(account.equity)
                # risk += mt5.order_calc_profit(orderType, self.asset, i.volume, i.price_open, i.sl)
                # if risk == None:
                #     return account.equity
                # else:
                return risk

    def portfolio_risk(self, account: Account) -> None:
        """Returns capital at risk as a percentage of equity."""
        
        pRisk = self.capital_risk(account) / account.equity

        return abs(pRisk)

    def capital_gain(self, account: Account):
        """Returns the $ amount gained if TP is filled.
        If no TP is set, returns account equity."""

        if self.trades == 1:                                #For one trades/asset
            if self.open_positions[0].type == 0:            #For long positions
                orderType = mt5.ORDER_TYPE_BUY
            else:                                           #For short positions
                orderType = mt5.ORDER_TYPE_SELL

            #________Calculating capital gain_________#
            # try:
            #     gain = mt5.order_calc_profit(orderType, self.asset, self.open_positions[0].volume, self.open_positions[0].price_open, self.open_positions[0].tp)
            # except TypeError:
            #     gain = account.equity
            gain = mt5.order_calc_profit(orderType, self.asset, self.open_positions[0].volume, self.open_positions[0].price_open, self.open_positions[0].tp)
            if gain == None:
                return account.equity
            else:
                return gain

        else:                                               #For > one trades/asset
            gain = 0
            for i in self.open_positions:
                
                if i.type == 0:
                    orderType = mt5.ORDER_TYPE_BUY
                else:
                    orderType = mt5.ORDER_TYPE_SELL

                #________Calculating capital gain_________#
                try:
                    gain += mt5.order_calc_profit(orderType, self.asset, i.volume, i.price_open, i.tp)
                except TypeError:
                    gain = account.equity
                # gain += mt5.order_calc_profit(orderType, self.asset, i.volume, i.price_open, i.tp)
                # if gain == None:
                #     return account.equity
                # else: return gain
                return gain

    def portfolio_gain(self, account: Account) -> None:
        """Returns capital target as a percentage of equity."""
        
        pGain = self.capital_gain(account) / account.equity

        return abs(pGain)

    def swap(self):
        """Returns the swap paid or received on all trades of an asset."""

        if self.trades == 1:
            return self.open_positions[0].swap
        else:
            swap = 0
            for i in self.open_positions:
                swap += i.swap
            return swap

    def swap_rate(self, account: Account) -> None:
        """Returns the swap paid or received as a percentage of capital target."""

        swap_ = self.swap() / self.capital_gain(account)

        return swap_

    def profit(self):
        '''Returns Gross profit on the position'''

        if self.trades == 1:
            profit = self.open_positions[0].profit
            return profit
        else:
            profit = 0
            for i in self.open_positions:
                profit += i.profit
            return profit

#_____________________Creating Order class_____________________#
class Order():
    """Returns or calculates various parameters of a single pending order.
    
    Attr:
        ticket: A unique id number given to every pending order in MT5"""

    def __init__(self, ticket):
        self.pending_orders = mt5.orders_get(ticket=ticket)
        self.symbol = self.pending_orders[0].symbol
        self.entry = self.pending_orders[0].price_open
        self.stop_loss = self.pending_orders[0].sl
        self.take_profit = self.pending_orders[0].tp
        self.comment = self.pending_orders[0].comment
        self.volume = self.pending_orders[0].volume_current

    @staticmethod
    def _fxAdjust(exposure, pair):
        """Converts the passed exposure in USD"""
        
        if pair[0:3] == 'USD':
            adjustedExpo = exposure / mt5.symbol_info_tick(pair).ask
        else:
            adjustedExpo = exposure * mt5.symbol_info_tick(pair).ask

        return adjustedExpo

    def position(self):

        string = ''
        if self.pending_orders[0].type in [0, 2, 4, 6]:
            string = 'Long'
        elif self.pending_orders[0].type in [1, 3, 5, 7]:
            string = 'Short'
        else:
            string = 'Close by'

        return string

    def real_volume(self):

        raw_volume = self.pending_orders[0].volume_current

        if self.symbol[0:3] in forex:
            return raw_volume * 100000
        elif self.symbol[0:3] in commodity:
            return raw_volume * 100
        elif self.symbol[0:3] == 'XAG':
            return raw_volume * 1000
        else:
            return raw_volume

    def exposure(self):
        """Gives the exposure denominated in USD.
           note: the forex rate is current & not 
           from the time @ which trade was executed"""

        raw_exposure = self.real_volume() * self.entry

        if self.symbol[0:3] == 'USD':                                    #Asset with USD base
            return self.real_volume()

        elif self.symbol in list1:                                       #A non-dollar denominated asset
            fx_expo = self._fxAdjust(raw_exposure, list1[self.symbol])
            return fx_expo

        else:                                                           #Dollar denominated asset
            return raw_exposure

    def leverage(self, account: Account) -> None:
        """Calculates implied leverage on that order"""

        lev = self.exposure() / account.free_margin

        return lev

    def _type(self):
        """Sets the order type of order for calculating profit"""

        if self.pending_orders[0].type in [0, 2, 4, 6]:
            type_  = mt5.ORDER_TYPE_BUY
        elif self.pending_orders[0].type in [1, 3, 5, 7]:
            type_ = mt5.ORDER_TYPE_SELL
        else:
            type_ = mt5.ORDER_TYPE_CLOSE_BY

        return type_

    def capital_risk(self, account: Account) -> None:
        """Returns the $ amount lost if SL is hit"""

        risk = mt5.order_calc_profit(self._type(), self.symbol, self.volume, self.entry, self.stop_loss)

        if risk is None:
            return -(account.equity)
        else:
            return risk

    def capital_target(self, account: Account) -> None:
        """Returns the $ amount that will be received if TP is hit"""

        target = mt5.order_calc_profit(self._type(), self.symbol, self.volume, self.entry, self.take_profit)

        if target is None:
            return account.equity
        else:
            return target

    def swap(self):
        """Returns the swap that you will pay or receive in USD after taking that position."""

        if self.symbol[-1: -5: -1] in ['ESYN', 'SAN.']:                 #Calculaing swap for Shares and ETFs
            if self.position() == 'Long':
                swap_rate = mt5.symbol_info(self.symbol).swap_long
            elif self.position() == 'Short':
                swap_rate = mt5.symbol_info(self.symbol).swap_short

            swapPerDay = ((self.exposure() * swap_rate) / 100) / 365
            
            return swapPerDay

        else:                                                           #Calculating swap for forex, commodities, index.
            if self.position() == 'Long':
                swap_rate = mt5.symbol_info(self.symbol).swap_long
            elif self.position() == 'Short':
                swap_rate = mt5.symbol_info(self.symbol).swap_short

            swapPerDay = swap_rate * self.volume

            if self.symbol[0:3] == 'USD':
                adjustedSwap = swapPerDay / mt5.symbol_info_tick(self.symbol).ask
                return adjustedSwap
            elif self.symbol in list1:
                return self._fxAdjust(swapPerDay, list1[self.symbol])
            else:
                return swapPerDay

    def margin(self):
        """Returns the required margin in $ to take that position."""

        rMargin = mt5.order_calc_margin(self._type(), self.symbol, self.volume, self.entry)

        return rMargin

    def expiry(self):
        """Returns the expiry date of the order if it has any,
            else returns 'GTC' for Good Till Cancel."""

        stamp = self.pending_orders[0].time_expiration
        if stamp == 0:
            return 'GTC'
        else:
            return dt.datetime.fromtimestamp(stamp).strftime("%d/%b/%y | %I:%M %p")

#_________Test__________#
if __name__ == "__main__":
    j = Account()

    k = Position('JGB10Y_M1')               #Insert asset name from MT5 as string
    print("-------Position-------")
    print(f"Asset name: {k.asset}")
    print(f"Net Entry Price: {k.entry_price()}")
    print(f"Current Price: {k.current_price}")
    print(f"Net Volume: {k.real_volume()}")
    print(f"Position: {k.position()}")
    print(f'Net real Exposure: {k.real_exposure()}')
    print(f'Net Adjusted Exposure: ${k.adjusted_exposure():.2f}')
    print(f'Leverage: {k.leverage(j):.2f}')
    print(f"Net Appriciation: {k.appriciation() * 100:.2f}%")
    print(f"Status: {k.status()}")
    print(f"Capital @ Risk: ${k.capital_risk(j):.2f}")
    print(f"Portfolio at Risk: {k.portfolio_risk(j) * 100:.2f}%")
    print(f"Potential gain: ${k.capital_gain(j):.2f}")
    print(f"Portfolio gain: {k.portfolio_gain(j) * 100:.2f}%")
    print(f"Current P/L: {k.profit():.3f}")
    print(f"Swap: {k.swap():.2f}")
    print(f"Number of open Trades: {k.trades}\n")

    m = Order(117216637)                     #Insert a ticket number from MT5
    print("-------Pending order-------")
    print(f"Symbol: {m.symbol}")
    print(f"Position: {m.position()}")
    print(f"Volume: {m.real_volume():.0f}")
    print(f"Exposure: ${m.exposure()}")
    print(f"Leverage: {m.leverage(j):.2f}")
    print(f"Capital @ Risk: ${m.capital_risk(j)}")
    print(f"Capital Target: ${m.capital_target(j)}")
    print(f"Swap/day: ${m.swap():.3f}")
    print(f"Required Margin: ${m.margin()}")
    print(f"Expiry: {m.expiry()}")
    print(f"Comment: {m.comment}")

mt5.shutdown()