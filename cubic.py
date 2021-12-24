from simulator import Strategy
import numpy as np
import warnings
warnings.simplefilter('ignore', np.RankWarning)

class Box(Strategy):

    def __init__(self) -> None:
        super().__init__()
        self.window_size = 20
        self.stop_loss = None

    def query(self, time):
        if time < self.window_size:
            return

        prices = [self.history[t].close for t in range(time-self.window_size, time)]
        times = range(len(prices))
        model = np.poly1d(np.polyfit(times, prices, 2))
        a, b, c = model.coefficients
        midpoint = -b / (2 * a)
        net_extrema_gehad = len(prices)*8//10 < midpoint and midpoint < len(prices)*1
        dippie = a > 0 and net_extrema_gehad
        toppie = a < 0 and net_extrema_gehad

        if self.usdt > 0 and dippie and abs(a) > 0.00000000005:
            self.market_buy()
            self.buy_price = prices[-1]
        elif self.btc > 0 and prices[-1]/self.buy_price > 1.005:
            self.market_sell()
        elif self.btc > 0 and prices[-1]/self.buy_price < 0.997:
            self.market_sell()

file = 'tracker/SPOT_BTC_USDT_1m.csv'
# file = 'tracker/SPOT_ETH_USDT_1m.csv'
# file = 'data/gemini_BTCUSD_2019_1min.csv'
# file = 'data/gemini_BTCUSD_2018_1min.csv'
# file = 'data/gemini_BTCUSD_2017_1min.csv'
# file = 'data/gemini_BTCUSD_2016_1min.csv'
# file = 'data/gemini_BTCUSD_2015_1min.csv'
strategy = Box()
strategy.run(file)