from simulator import Strategy

class Box(Strategy):

    def __init__(self) -> None:
        super().__init__()
        self.window_size = 60*12
        self.stop_loss = None
        self.penalty = None
        self.trigger = None

    def query(self, time):
        if time < self.window_size:
            return None, []

        price = [self.history[t].close for t in range(time-self.window_size,time)]
        sprice = sorted(price)
        i = len(sprice) // 4
        j = 3 * i
        k = i // 3
        m = j + 5
        low = sprice[i]
        high = sprice[j]
        superlow = sprice[k]
        superhigh = sprice[m]

        if price[-1] > superhigh:
            self.trigger = True
        if self.penalty is not None and self.penalty < time:
            self.penalty = None
        if self.usdt and price[-1] < low and superlow < price[-1] and abs(price[-60] / price[-1]) < 1 and not self.penalty:
            self.market_buy()
            self.stop_loss = price[-1] * 0.98
        elif self.btc and self.stop_loss is not None and price[-1] < self.stop_loss:
            self.market_sell()
            self.penalty = time + self.window_size * 2 
        elif self.btc and price[-1] < high and self.trigger:
            self.market_sell()
            self.trigger = None

file = 'tracker/SPOT_BTC_USDT_1m.csv'
# file = 'tracker/SPOT_ETH_USDT_1m.csv'
# file = 'data/gemini_BTCUSD_2019_1min.csv'
# file = 'data/gemini_BTCUSD_2018_1min.csv'
# file = 'data/gemini_BTCUSD_2017_1min.csv'
# file = 'data/gemini_BTCUSD_2016_1min.csv'
# file = 'data/gemini_BTCUSD_2015_1min.csv'
strategy = Box()
strategy.run(file)