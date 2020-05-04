def netexposure(trade, current):
    """Gives net exposure & P/L

    Parameters:
        trade: A list of lists containing entry price and lot sizes of each asset
        current: current price of asset"""
    current_price = current

    #________Calculating volume_________#
    total_shares = 0
    for j in trade:
        total_shares += j[1]

    #________calculating exposure_________#
    cumulatuve_exposure = 0
    for i in trade:
        cumulatuve_exposure += i[0] * i[1]

    #________Calculating entry price_______#
    if total_shares == 0:
        sum_ = 0
        for i in trade:
            sum_ += i[0]
        entry_price = sum_ / len(trade)
    elif total_shares != 0:
        entry_price = cumulatuve_exposure/total_shares

    #________Calculating Gross Profit_________#
    if total_shares == 0:
        profit = -(cumulatuve_exposure)
    else:
        profit = (current_price - entry_price) * total_shares

    return f"Exposure: {abs(cumulatuve_exposure)}, Lot size: {total_shares}, Entry: {entry_price:.4f}, Profit: {profit:.2f}"

trades = [[100, 10], [105, -10], [120, -20]]
k = netexposure(trades, 130)
print(k)