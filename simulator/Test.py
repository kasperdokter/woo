from simulator import PlatformSimulator, Order, BUY, SELL, LIMIT, MARKET
import numpy as np
import matplotlib.pyplot as plt
import warnings




# DEZE STRATEGIE GAAT NIET WERKEN

warnings.simplefilter('ignore', np.RankWarning)

def get_time_price(history, window_size=0):
    time = [row.timestamp for row in history[-window_size:]]
    price = [row.open for row in history[-window_size:]]
    return time, price

def get_model(price, degree):
    coefficients = np.polyfit(range(len(price)), price, degree)
    polynomial = np.poly1d(coefficients) # polynomials can be evaluated easily
    return polynomial

def plot(time, price, model, title=None):
    plt.plot(time, price)
    plt.plot(time, model(range(len(price))))
    plt.title(title or f'{time[0]} to {time[-1]}')
    plt.show()

class BoxStrategy:

    def __init__(self, history) -> None:
        self.history = history
        self.stop_loss = None
        self.penalty = None
        self.trigger = None

    def get_orders(self, time, orders, btc, usdt):

        window_size = 60*12

        if time < window_size:
            return None, []

        # long term trend
        # time, price = get_time_price(self.history[:time], window_size)
        price = [self.history[t].open for t in range(time-window_size,time)]
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
        if usdt and price[-1] < low and superlow < price[-1] and abs(price[-60] / price[-1]) < 1 and not self.penalty:
            order = Order(BUY, MARKET, None)
            self.stop_loss = price[-1] * 0.98
        elif btc and self.stop_loss is not None and price[-1] < self.stop_loss:
            order = Order(SELL, MARKET, None)
            self.penalty = time + window_size * 2 
        elif btc and price[-1] < high and self.trigger:
            order = Order(SELL, MARKET, None)
            self.trigger = None
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