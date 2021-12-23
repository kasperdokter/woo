from simulator import PlatformSimulator, Order, BUY, SELL, LIMIT, MARKET, strtime
import numpy as np
import matplotlib.pyplot as plt
import warnings

warnings.simplefilter('ignore', np.RankWarning)

def get_time_price(history, window_size=0):
    time = [row.timestamp for row in history[-window_size:]]
    price = [row.open for row in history[-window_size:]]
    return time, price

def get_model(time, price, degree):
    coefficients = np.polyfit(range(len(price)), price, degree)
    polynomial = np.poly1d(coefficients) # polynomials can be evaluated easily
    return polynomial

def plot(time, price, model, title=None):
    plt.plot(time, price)
    plt.plot(time, model(range(len(price))))
    plt.title(title or f'{strtime(time[0])} to {strtime(time[-1])}')
    plt.show()

class BoxStrategy:

    def __init__(self, history) -> None:
        self.history = history
        self.stoploss = None

    def get_orders(self, time, orders, btc, usdt):

        if time < 60*12:
            return None, []

        # long term trend
        window_size = 60*12
        time, price = get_time_price(self.history[:time], window_size)
        model1 = get_model(price, 1)
        trend1 = model1(time)
        a, b = model1.coefficients

        # Min en max afwijking van trend
        delta = [price[i] - trend1[i] for i in range(len(price))] 
        laag = min(delta)
        hoog = max(delta)
        nu = delta[-1]

        # Wacht op een dippie of toppie
        # short_window_size = 5
        # time2, price2 = get_time_price(history, short_window_size)
        # model2 = get_model(time2, price2, 2)
        # a, b, c = model2.coefficients
        # now = time[-1]
        # midpoint = -b / (2 * a)
        # dippie = a > 0 and now - 60 < midpoint and midpoint < now
        # if dippie:
        #     plot(time2, price2, model2, 'dippie?')

        if usdt and abs(a) < 0.0001 and nu < laag + (hoog - laag) / 5 and price[-2] - price[-1] < 0:
            # plot(time, price, model1, title='kopen')
            order = Order(BUY, MARKET, None)
            self.stop_loss = price[-1] * 0.95
        elif btc and price[-1] < self.stop_loss:
            # plot(time, price, model, title='verkopen (stoploss)')
            order = Order(SELL, MARKET, None)
        elif btc and nu > hoog - (hoog - laag) / 5 and price[-2] - price[-1] > 0:
            # plot(time, price, model, title='verkopen')
            order = Order(SELL, MARKET, None)
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