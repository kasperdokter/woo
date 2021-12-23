from simulator import PlatformSimulator, Order, BUY, SELL, LIMIT, MARKET
import numpy as np
import matplotlib.pyplot as plt
import warnings

# DEZE STRATEGIE GEEFT GEEN WINST

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
        self.stoploss = None

    def get_orders(self, time, orders, btc, usdt):
        if time < 60:
            return None, []

        # Wacht op een dippie of toppie
        window_size = 20
        time, price = get_time_price(self.history[:time], window_size)
        model = get_model(price, 2)
        # if tijd % 1000 == 0:
            # plot(time, price, model)
        a, b, c = model.coefficients
        midpoint = -b / (2 * a)
        net_extrema_gehad = len(price)-10 < midpoint and midpoint < len(price)-8
        dippie = a > 0 and net_extrema_gehad
        toppie = a < 0 and net_extrema_gehad

        if usdt > 0 and dippie and abs(a) > 0.00000000005:
            # plot(time, price, model, 'dippie?')
            order = Order(BUY, MARKET, None)
            self.buy_price = price[-1]
        elif btc > 0 and price[-1]/self.buy_price > 1.005:
            # plot(time, price, model, 'toppie?')
            order = Order(SELL, MARKET, None)
        elif btc > 0 and price[-1]/self.buy_price < 0.997:
            # plot(time, price, model, 'toppie?')
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