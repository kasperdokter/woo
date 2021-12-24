import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math
from enum import Enum

class OrderType(Enum):
    LIMIT = 0
    MARKET = 1

class OrderSide(Enum):
    BUY = 0
    SELL = 1

class Order:

    def __init__(self, side: OrderSide, type: OrderType, price: float):
        self.side = side
        self.type = type
        self.price = price # btc / usdt

    def __str__(self):
        return f"{self.side} {self.type} {self.price} btc/usdt"

    def __hash__(self) -> int:
        return hash(tuple(self.side, self.type, self.price))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return False
        return self.side == other.side and self.type == other.type and self.price == other.price

class Period:

    def __init__(self, timestamp_milliseconds, open, high, low, close) -> None:
        self.timestamp = datetime.utcfromtimestamp(int(timestamp_milliseconds)/1000)
        self.open = float(open)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)

    def strtime(self):
        """ Convert UNIX timestamp into human-readable format """
        return self.timestamp.strftime('%Y-%m-%d %H:%M:%S')

class Strategy:

    def __init__(self): 
        self.history: list[Period] = []
        self.pending: list[Order] = []
        self.btc: float = 0
        self.usdt: float = 0

    def query(self, time: int):
        """ Update the list of pending orders, based on the price observations
        self.history[:time] of the prices until (not including) the price at
        index time."""
        raise NotImplementedError('Make sure to override the "query" method in the strategy class.')

    def market_buy(self):
        self.pending.append(Order(OrderSide.BUY, OrderType.MARKET, None))

    def market_sell(self):
        self.pending.append(Order(OrderSide.SELL, OrderType.MARKET, None))
    
    def limit_buy(self, price):
        self.pending.append(Order(OrderSide.BUY, OrderType.LIMIT, price))
    
    def limit_sell(self, price):
        self.pending.append(Order(OrderSide.SELL, OrderType.LIMIT, price))
        
    def run(self, filename: str):
        """ Runs this strategy with data from the given csv file. """

        # Load the data from the csv
        with open(filename, newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            header = next(csv_reader)
            self.history = [
                Period(
                    int(row[header.index('timestamp')]), 
                    float(row[header.index('open')]), 
                    float(row[header.index('high')]), 
                    float(row[header.index('low')]), 
                    float(row[header.index('close')])
                ) 
                for row in csv_reader
            ]
        
        # Reverse data if necessary
        if self.history[0].timestamp > self.history[1].timestamp:
            self.history = list(reversed(self.history))
    
        # Set the initial balance
        self.usdt = 10 ** math.floor(math.log10(self.history[0].open))

        # For plotting
        times = []
        prices = []
        balance = []
        buy_times = []
        buy_prices = []
        sell_times = []
        sell_prices = []

        # Loop through the entries
        for time, period in enumerate(self.history):

            # Query the strategy to create new and/or canceled orders
            self.query(time)

            # Try to fill the pending orders in the current entry
            completed = []
            for order in self.pending:
                if order.side == OrderSide.BUY:
                    if order.type == OrderType.MARKET:
                        price = period.open
                    elif order.type == OrderType.LIMIT:
                        if order.price >= period.low:
                            price = order.price
                        else:
                            continue
                    self.btc += self.usdt / price
                    self.usdt = 0
                    completed.append(order)
                    buy_times.append(period.timestamp)
                    buy_prices.append(price)
                elif order.side == OrderSide.SELL:
                    if order.type == OrderType.MARKET:
                        price = period.open
                    elif order.type == OrderType.LIMIT:
                        if order.price <= period.high:
                            price = order.price
                        else:
                            continue
                    self.usdt += self.btc * price
                    self.btc = 0
                    completed.append(order)
                    sell_times.append(period.timestamp)
                    sell_prices.append(price)

            # Remove the completed orders
            for order in completed:
                self.pending.remove(order)

            # Compute the current balance at the end of this minute
            curr_balance = self.usdt + self.btc * period.close

            # Give an balance update, every day
            if time % (60 * 24) == 0:
                print(period.strtime(), 'usdt', curr_balance, end='\r')
        
            # Add it to the plot
            times.append(period.timestamp)
            prices.append(period.close)
            balance.append(curr_balance)

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