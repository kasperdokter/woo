from simulator import PlatformSimulator, Order, BUY, SELL, LIMIT, MARKET

class Erik:

    def __init__(self) -> None:
        pass

    def get_orders(self, history, orders, btc, usdt, time):
        if len(history) < 2:
            return None, []
        amplitude = 1000
        open = history[0][1]
        close = history[1][1]
        delta = close - open
        if abs(delta) < amplitude and usdt > 0:
            order = Order(BUY, MARKET, close)
        elif abs(delta) > amplitude and btc > 0:
            order = Order(SELL, MARKET, close)
        else:
            order = None
        return order, orders

WOO = PlatformSimulator('simulator/SPOT_BTC_USDT_1m.csv')
WOO.run(Erik())