import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math



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

class Entry:

    def __init__(self, timestamp_milliseconds, open, high, low) -> None:
        self.timestamp = datetime.utcfromtimestamp(int(timestamp_milliseconds)/1000)
        self.open = float(open)
        self.high = float(high)
        self.low = float(low)

    def strtime(self):
        """ Convert UNIX e.timestamp into human-readable format """
        return self.timestamp.strftime('%Y-%m-%d %H:%M:%S')


class PlatformSimulator:

    def __init__(self, filename, btc=0, usdt=100):
        self.filename = filename
        self.rows = None
        self.orders: list[Order] = []
        self.btc = btc
        self.usdt = usdt

    def run(self, strategy_class):

        # Load the data from the csv
        with open(self.filename, newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            header = next(csv_reader)
            open_idx = header.index('open')
            high_idx = header.index('high')
            low_idx = header.index('low')
            timestamp_idx = header.index('timestamp')
            self.rows = [
                Entry(row[timestamp_idx], row[open_idx], row[high_idx], row[low_idx]) 
                for row in csv_reader
            ]
        
        # Reverse data if necessary
        if self.rows[0].timestamp > self.rows[1].timestamp:
            self.rows = list(reversed(self.rows))
    
        # Set the initial balance
        self.usdt = 10 ** math.floor(math.log10(self.rows[0].open))

        # Initialize strategy
        strategy = strategy_class(self.rows)

        # For plotting
        times = []
        prices = []
        balance = []
        buy_times = []
        buy_prices = []
        sell_times = []
        sell_prices = []

        # Loop through the entries
        for t, entry in enumerate(self.rows):

            # Compute the current balance
            curr_balance = self.usdt + self.btc * entry.open
        
            # Add it to the plot
            times.append(entry.timestamp)
            prices.append(entry.open)
            balance.append(curr_balance)

            # Give an balance update, every day
            if t % (60 * 24) == 0:
                print(entry.strtime(), 'usdt', curr_balance, end='\r')

            # Query the strategy for new and/or canceled orders
            order, cancelled = strategy.get_orders(t, self.orders, self.btc, self.usdt)
            for x in cancelled:
                self.orders.remove(x)
            if order is not None:
                self.orders.append(order)

            # Try to fill the pending orders in the current entry
            completed = []
            for order in self.orders:
                if order.length == BUY:
                    if order.kind == MARKET:
                        price = entry.open
                    elif order.kind == LIMIT:
                        if order.price >= entry.low:
                            price = order.price
                        else:
                            continue
                    self.btc += self.usdt / price
                    self.usdt = 0
                    completed.append(order)
                    buy_times.append(entry.timestamp)
                    buy_prices.append(price)
                elif order.length == SELL:
                    if order.kind == MARKET:
                        price = entry.open
                    elif order.kind == LIMIT:
                        if order.price <= entry.high:
                            price = order.price
                        else:
                            continue
                    self.usdt += self.btc * price
                    self.btc = 0
                    completed.append(order)
                    sell_times.append(entry.timestamp)
                    sell_prices.append(price)

            # Remove the completed orders
            for order in completed:
                self.orders.remove(order)

        # Plot
        locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
        formatter = mdates.ConciseDateFormatter(locator)
        plt.gca().xaxis.set_major_locator(locator)
        plt.gca().xaxis.set_major_formatter(formatter)
        plt.plot(times, prices, zorder=-1)
        plt.plot(times, balance, zorder=-1)
        plt.scatter(buy_times, buy_prices, c='green')
        plt.scatter(sell_times, sell_prices, c='red')
        plt.show()