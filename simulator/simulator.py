import csv
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

# Convert UNIX timestamp into human-readable format
def strtime(timestamp_milliseconds):
    return datetime.utcfromtimestamp(int(timestamp_milliseconds)/1000).strftime('%Y-%m-%d %H:%M:%S')

LIMIT = 0
MARKET = 1

def kind_str(k):
    return 'LIMIT' if k == 0 else 'MARKET'

BUY = 0
SELL = 1

def length_str(k):
    return 'BUY' if k == 0 else 'SELL'

class Memory:
    pass

class Order:

    def __init__(self, length, kind, price):
        self.length = length
        self.kind = kind
        self.price = price # btc / usdt

    def __str__(self):
        return f"{length_str(self.length)} {kind_str(self.kind)} {self.price} btc/usdt"

class PlatformSimulator:

    def __init__(self, filename, btc=0, usdt=100):
        self.filename = filename
        self.rows = None
        self.orders = []
        self.btc = btc
        self.usdt = usdt

    def run(self, strategy):
        with open(self.filename, newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            self.rows = [tuple(float(x) for x in row) for row in csv_reader]

        # For plotting
        times = []
        prices = []
        buy_times = []
        buy_prices = []
        sell_times = []
        sell_prices = []
            
        for t in range(len(self.rows)):
            times.append(t)

            # amount,close,end_timestamp,high,low,open,start_timestamp,volume
            _, t_open, _, _, _, _, _, _ = self.rows[t-1]
            _, _, _, t_high, t_low, _, t_start_timestamp, _ = self.rows[t]

            prices.append(t_open)


            # print('--- ', strtime(t_start_timestamp))
            # print(t_open, t_high, t_low)

            order, cancelled = strategy.get_orders(self.rows[:t], self.orders, self.btc, self.usdt, t)
            for x in cancelled:
                # print(f"CANCEL order {x}")
                self.orders.remove(x)
            if order is not None:
                # print(f"PENDING order {order}")
                self.orders.append(order)

            completed = []
            for order in self.orders:
                if order.length == BUY:
                    if order.kind == MARKET:
                        price = t_open
                    elif order.kind == LIMIT:
                        if order.price >= t_low:
                            price = order.price
                        else:
                            continue
                    self.btc += self.usdt / price
                    self.usdt = 0
                    completed.append(order)
                    buy_times.append(t)
                    buy_prices.append(price)
                elif order.length == SELL:
                    if order.kind == MARKET:
                        price = t_open
                    elif order.kind == LIMIT:
                        if order.price <= t_high:
                            price = order.price
                        else:
                            continue
                    self.usdt += self.btc * price
                    self.btc = 0
                    completed.append(order)
                    sell_times.append(t)
                    sell_prices.append(price)

            for order in completed:
                # print(f"FILLED order {order}")
                self.orders.remove(order)
            
        print('usdt', self.usdt + self.btc * self.rows[-1][5])

        plt.plot(times, prices, zorder=-1)
        plt.scatter(buy_times, buy_prices, c='green')
        plt.scatter(sell_times, sell_prices, c='red')
        plt.show()