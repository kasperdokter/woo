from simulator import PlatformSimulator, Order, BUY, SELL, LIMIT, MARKET, strtime
import numpy as np
import matplotlib.pyplot as plt
import warnings

warnings.simplefilter('ignore', np.RankWarning)

def get_time_price(history, window_size=0):
    time = [row[2] for row in history[-window_size:]]
    price = [row[1] for row in history[-window_size:]]
    return time, price

def get_model(time, price, degree):
    coefficients = np.polyfit(time, price, degree)
    polynomial = np.poly1d(coefficients) # polynomials can be evaluated easily
    return polynomial

def plot(time, price, model, title=None):
    plt.plot(time, price)
    plt.plot(time, model(time))
    plt.title(title or f'{strtime(time[0])} to {strtime(time[-1])}')
    plt.show()

class BoxStrategy:

    def __init__(self) -> None:
        self.stoploss = None

    def get_orders(self, history, orders, btc, usdt, tijd):
        if len(history) < 60:
            return None, []

        # Wacht op een dippie of toppie
        window_size = 20
        time, price = get_time_price(history, window_size)
        model = get_model(time, price, 2)
        # if tijd % 1000 == 0:
            # plot(time, price, model)
        a, b, c = model.coefficients
        midpoint = -b / (2 * a)
        net_extrema_gehad = time[-10] < midpoint and midpoint < time[-8]
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

WOO = PlatformSimulator('simulator/SPOT_BTC_USDT_1m.csv')
WOO.run(BoxStrategy())