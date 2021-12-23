from simulator import PlatformSimulator, Order, BUY, SELL, LIMIT, MARKET
import numpy as np
import matplotlib.pyplot as plt
import warnings


# DEZE STRATEGIE WERK EEN BEETJE

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

    def get_orders(self, time, orders, btc, usdt):

        window_size = 60*24*2

        if time < window_size:
            return None, []

        # long term trend
        time, price = get_time_price(self.history[:time], window_size)
        sprice = sorted(price)
        i = len(sprice) // 4
        j = 3 * i
        k = i // 3
        low = sprice[i]
        high = sprice[j]
        superlow = sprice[k]

        if usdt and price[-1] < low and superlow < price[-1] and abs(price[-60] / price[-1]) < 1:
            order = Order(BUY, MARKET, None)
            self.stop_loss = price[-1] * 0.98
        elif btc and self.stop_loss is not None and price[-1] < self.stop_loss:
            order = Order(SELL, MARKET, None)
        elif btc and price[-1] > high:
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