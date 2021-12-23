from simulator import PlatformSimulator, Order, BUY, SELL, LIMIT, MARKET


# DEZE STRATEGIE HEEFT BUGS

class BoxStrategy:

    def __init__(self, history, time=0) -> None:
        self.history = history
        self.time = time
        self.penalty = None
        self.max_profit = None
        self.buy_price = None

    def get_orders(self, time, orders, btc, usdt):

        window_size = 60*24*2

        if time < window_size:
            return None, []
        
        price_60 = self.history[time-60].open
        last_price = self.history[time-1].open

        price = [self.history[t].open for t in range(time-window_size, time)]
        price.sort()
       
        i = len(price) // 4
        j = 3 * i
        k = i // 3
        low = price[i]
        high = price[j]
        superlow = price[k]

        if btc and last_price > high:
            self.max_profit = max(last_price / self.buy_price, self.max_profit)

        if usdt and last_price < low and superlow < last_price and abs(price_60 / last_price) < 1 and (self.penalty is None or self.penalty < time):
            order = Order(BUY, MARKET, None)
            self.buy_price = last_price
        elif btc and self.buy_price is not None and last_price < self.buy_price * 0.98:
            order = Order(SELL, MARKET, None)
            # self.penalty = time + window_size // 2
            self.buy_price = None
        elif btc and last_price > high:
            order = Order(SELL, MARKET, None)
            self.buy_price = None
        else:
            order = None

        return order, []

file = 'tracker/SPOT_BTC_USDT_1m.csv'
# file = 'tracker/SPOT_ETH_USDT_1m.csv'
# file = 'data/gemini_BTCUSD_2019_1min.csv'
# file = 'data/gemini_BTCUSD_2018_1min.csv'
# file = 'data/gemini_BTCUSD_2017_1min.csv'
# file = 'data/gemini_BTCUSD_2016_1min.csv'
# file = 'data/gemini_BTCUSD_2015_1min.csv'
WOO = PlatformSimulator(file)
WOO.run(BoxStrategy)