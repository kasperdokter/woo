from simulator import PlatformSimulator, Order, BUY, SELL, LIMIT, MARKET, strtime
import matplotlib.pyplot as plt

# HEEFT BUGS

def get_time_price(history, window_size=0):
    time = [row.timestamp for row in history[-window_size:]]
    price = [row.open for row in history[-window_size:]]
    return time, price

def plot(time, price, model=None, title=None):
    plt.plot(time, price)
    if model:
        plt.plot(time, model(range(len(price))))
    plt.title(title)
    plt.show()

class Interval:

    def __init__(self, a, b) -> None:
        self.a = a
        self.b = b

    def __add__(self, x):
        return Interval(self.a + x, self.b + x)

    def __sub__(self, x):
        return Interval(self.a - x, self.b - x)

    def __mul__(self, x):
        return Interval(self.a * x, self.b * x)

    def __truediv__(self, x):
        return Interval(self.a / x, self.b / x)

    def __contains__(self, x):
        return min(self.a, self.b) <= x and x <= max(self.a, self.b)

    def __len__(self):
        return abs(self.b - self.a)

    def __repr__(self) -> str:
        return f"[{min(self.a,self.b)},{max(self.a, self.b)}]"

class BoxStrategy:

    def __init__(self) -> None:
        self.stoploss = None

    def get_orders(self, history, orders, btc, usdt, tijd):

        window_size = 60
        if len(history) < window_size:
            return None, []

        time, prices = get_time_price(history)

        while True:
            window_size += 60 * 48

            if len(history) < window_size:
                return None, []

            p = prices[-window_size:]
            high = max(p)
            low = min(p)
            height = high - low

            if high / low < 1.05:
                continue

            swings = 0
            prev_event = None
            for price in prices:
                if price < low + height / 5:
                    if prev_event == 'high':
                        swings += 1
                    prev_event = 'low'
                if price > high - height / 5:
                    if prev_event == 'low':
                        swings += 1
                    prev_event = 'high'

            if swings >= 2:
                break
        
        print(window_size, tijd)

        low = min(prices)
        high = max(prices)
        price = prices[-1]

        a = high - low
        buy = Interval(0.1, 0.2) * a + low
        stop = Interval(-0.1, -0.2) * a + low
        sell = Interval(0.8, 0.9) * a + low


        if usdt and price in buy:
            # print(a, Interval(0.1, 0.2) * a, buy, price, Interval(low, high))
            # plot(time, prices, None, None)
            order = Order(BUY, MARKET, None)
        elif btc and price in stop:
            order = Order(SELL, MARKET, None)
            print('STOP!', tijd)
        elif btc and price in sell:
            order = Order(SELL, MARKET, None)
        else:
            order = None

        return order, []

WOO = PlatformSimulator('simulator/SPOT_BTC_USDT_1m.csv')
WOO.run(BoxStrategy())
