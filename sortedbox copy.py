from simulator import Strategy

class Box(Strategy):

    def __init__(self) -> None:
        super().__init__()
        self.window_size = 60*24*2
        self.penalty = None
        self.max_profit = 1
        self.buy_price = None

    def query(self, time):
        if time < self.window_size:
            return None, []
        
        price_60 = self.history[time-60].open
        last_price = self.history[time-1].open

        price = [self.history[t].open for t in range(time-self.window_size, time)]
        price.sort()
       
        i = len(price) // 4
        j = 3 * i
        k = i // 3
        low = price[i]
        high = price[j]
        superlow = price[k]

        if self.btc and last_price > high:
            self.max_profit = max(last_price / self.buy_price, self.max_profit)

        if self.usdt and last_price < low and superlow < last_price and abs(price_60 / last_price) < 1 and (self.penalty is None or self.penalty < time):
            self.market_buy()
            self.buy_price = last_price
        elif self.btc and self.buy_price is not None and last_price < self.buy_price * 0.98:
            self.market_sell()
            # self.penalty = time + window_size // 2
            self.buy_price = None
        elif self.btc and last_price > high:
            self.market_sell()
            self.buy_price = None

file = 'tracker/SPOT_BTC_USDT_1m.csv'
# file = 'tracker/SPOT_ETH_USDT_1m.csv'
# file = 'data/gemini_BTCUSD_2019_1min.csv'
# file = 'data/gemini_BTCUSD_2018_1min.csv'
# file = 'data/gemini_BTCUSD_2017_1min.csv'
# file = 'data/gemini_BTCUSD_2016_1min.csv'
# file = 'data/gemini_BTCUSD_2015_1min.csv'
strategy = Box()
strategy.run(file)