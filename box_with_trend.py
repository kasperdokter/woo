from simulator import Strategy
import numpy as np

class BoxWithTrend(Strategy):

    def __init__(self) -> None:
        super().__init__()
        self.window_size = 60*48
        self.stop_loss = None

    def query(self, time):
        if time < self.window_size:
            return

        # long term trend
        prices = [self.history[t].close for t in range(time-self.window_size, time)]
        domain = range(len(prices))
        model = np.poly1d(np.polyfit(domain, prices, 1))
        trend = model(domain)
        a, b = model.coefficients

        # Min en max afwijking van trend
        delta = [prices[i] - trend[i] for i in range(len(prices))] 
        laag = min(delta)
        hoog = max(delta)
        nu = delta[-1]

        if self.usdt and nu < laag + (hoog - laag) / 5 and prices[-1] / min(prices[-10:]) < 1.01:
            self.market_buy()
            self.stop_loss = prices[-1] * 0.98
        elif self.btc and prices[-1] < self.stop_loss:
            self.market_sell()
        elif self.btc and nu > hoog - (hoog - laag) / 5 and max(prices[-10:]) / prices[-1] > 1.01:
            self.market_sell()

file = 'tracker/SPOT_BTC_USDT_1m.csv'
# file = 'tracker/SPOT_ETH_USDT_1m.csv'
# file = 'data/gemini_BTCUSD_2019_1min.csv'
# file = 'data/gemini_BTCUSD_2018_1min.csv'
# file = 'data/gemini_BTCUSD_2017_1min.csv'
# file = 'data/gemini_BTCUSD_2016_1min.csv'
# file = 'data/gemini_BTCUSD_2015_1min.csv'
strategy = BoxWithTrend()
strategy.run(file)