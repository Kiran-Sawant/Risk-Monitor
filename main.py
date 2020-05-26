import MetaTrader5 as mt5
import calculator as ca
import xlwings as xl
import time

mt5.initialize()

book = xl.Book('Book1.xlsx')

positionSheet = book.sheets('Positions')
orderSheet = book.sheets('Orders')
portfolioSheet = book.sheets('Portfolio')

while True:

    #____________Portfolio Sheet_____________#
    my_account = ca.Account()

    portfolioSheet.cells(2, 'B').value = my_account.name
    portfolioSheet.cells(3, 'B').value = my_account.server
    portfolioSheet.cells(4, 'B').value = my_account.mode()
    portfolioSheet.cells(5, 'B').value = my_account.equity
    portfolioSheet.cells(6, 'B').value = my_account.free_margin
    portfolioSheet.cells(7, 'B').value = my_account.margin
    portfolioSheet.cells(8, 'B').value = my_account.margin_level
    portfolioSheet.cells(9, 'B').value = my_account.balance
    portfolioSheet.cells(10, 'B').value = my_account.profit
    

    #____________Position Sheet________________#
    allPositions = mt5.positions_get()

    assets = set()

    for i in allPositions:
        assets.add(i.symbol)

    tempVar = 11 + len(assets)

    positionSheet.range('D11:U30').clear_contents()
    
    for i in range(11, tempVar + len(assets)):
        for symbol in assets:
            my_positions = ca.Position(symbol)


            positionSheet.cells(i, 'D').value = my_positions.position()
            positionSheet.cells(i, 'E').value = my_positions.asset
            positionSheet.cells(i, 'F').value = my_positions.entry_price()
            positionSheet.cells(i, 'G').value = abs(my_positions.real_volume())
            positionSheet.cells(i, 'H').value = abs(my_positions.adjusted_exposure())
            positionSheet.cells(i, 'I').value = my_positions.leverage(my_account)
            positionSheet.cells(i, 'J').value = my_positions.current_price
            positionSheet.cells(i, 'K').value = my_positions.capital_risk(my_account)
            positionSheet.cells(i, 'L').value = my_positions.portfolio_risk(my_account)
            positionSheet.cells(i, 'M').value = my_positions.capital_gain(my_account)
            positionSheet.cells(i, 'N').value = my_positions.portfolio_gain(my_account)
            positionSheet.cells(i, 'O').value = my_positions.status()
            positionSheet.cells(i, 'P').value = my_positions.appriciation()
            positionSheet.cells(i, 'Q').value = my_positions.swap()
            positionSheet.cells(i, 'R').value = my_positions.swap_rate(my_account)
            positionSheet.cells(i, 'S').value = my_positions.profit()
            positionSheet.cells(i, 'T').value = my_positions.profit()/my_account.balance
            positionSheet.cells(i, 'U').value = my_positions.trades

            assets.remove(symbol)
            break
    

    #_____________Orders Sheet___________________#
    allOrders = mt5.orders_get()

    tickets = set()

    for order in allOrders:
        tickets.add(order.ticket)
    
    tempVar2 = 11 + len(tickets)

    orderSheet.range('D11:S41').clear_contents()

    for i in range(11, tempVar2 + len(tickets)):
        for ticket in tickets:
            my_order = ca.Order(ticket)

            orderSheet.cells(i, 'D').value = my_order.position()
            orderSheet.cells(i, 'E').value = my_order.symbol
            orderSheet.cells(i, 'F').value = my_order.entry
            orderSheet.cells(i, 'G').value = my_order.real_volume()
            orderSheet.cells(i, 'H').value = my_order.exposure()
            orderSheet.cells(i, 'I').value = my_order.leverage(my_account)
            orderSheet.cells(i, 'J').value = my_order.capital_risk(my_account)
            orderSheet.cells(i, 'K').value = my_order.capital_risk(my_account) / my_account.equity
            orderSheet.cells(i, 'L').value = my_order.capital_target(my_account)
            orderSheet.cells(i, 'M').value = my_order.capital_target(my_account) / my_account.equity
            orderSheet.cells(i, 'N').value = my_order.swap()
            orderSheet.cells(i, 'O').value = my_order.swap() / my_order.capital_target(my_account)
            orderSheet.cells(i, 'P').value = my_order.margin()
            orderSheet.cells(i, 'Q').value = my_order.margin() / my_account.free_margin
            orderSheet.cells(i, 'R').value = my_order.expiry()
            orderSheet.cells(i, 'S').value = my_order.comment

            tickets.remove(ticket)
            break
    
    time.sleep(55)

mt5.shutdown()