from simulator import PlatformSimulator, Order, BUY, SELL, LIMIT, MARKET


# DEZE STRATEGIE HEEFT BUGS

class BoxStrategy:

    def __init__(self, history, time=0) -> None:
        self.history = history
        self.time = time
        self.stop_loss = None
        self.sprice = None
        self.min_index = None
        self.max_index = None
        self.penalty = None
        self.max_profit = None
        self.buy_price = None

    def get_orders(self, time, orders, btc, usdt):

        window_size = 60*24*2

        if time < window_size:
            return None, []
        
        price_60 = self.history[time-60].open
        last_price = self.history[time-1].open

        if self.sprice is None:
            price = [self.history[t].open for t in range(time-window_size, time)]
            self.sprice = list(enumerate(price))
            self.sprice.sort(key=lambda x:x[1])
            self.min_index = 0
            self.max_index = len(price) - 1
        else:
            for idx in range(len(self.sprice)):
                x = self.sprice[idx]
                if x[0] == self.min_index:
                    del self.sprice[idx]
                    break

            self.min_index += 1
            self.max_index += 1 
            y = (self.max_index, last_price)

            a = 0
            b = len(self.sprice) - 1

            if last_price <= self.sprice[a][1]:
                self.sprice.insert(a, y)
            elif last_price >= self.sprice[b][1]:
                self.sprice.append(y)
            else:
                while True:
                    if a + 1 == b:
                        self.sprice.insert(b, y)
                        # assert self.sprice[a][1] <= last_price                    
                        # assert self.sprice[b][1] >= last_price
                        break
                    m = (a + b) // 2
                    if self.sprice[m][1] == last_price:
                        self.sprice.insert(m, y)
                        break
                    if self.sprice[m][1] > last_price:
                        b = m
                    if self.sprice[m][1] < last_price:
                        a = m

        # for z in range(len(self.sprice)-1):
        #     assert self.sprice[z][1] <= self.sprice[z+1][1], z

        i = len(self.sprice) // 4
        j = 3 * i
        k = i // 3
        low = self.sprice[i][1]
        high = self.sprice[j][1]
        superlow = self.sprice[k][1]

        if btc and last_price > high:
            self.max_profit = max(last_price / self.buy_price, self.max_profit)

        if usdt and last_price < low and superlow < last_price and abs(price_60 / last_price) < 1 and (self.penalty is None or self.penalty < time):
            order = Order(BUY, MARKET, None)
            self.buy_price = last_price
        elif btc and self.buy_price is not None and last_price < self.buy_price * 0.98:
            order = Order(SELL, MARKET, None)
            # self.penalty = time + window_size // 2
            self.buy_price = None
        elif btc and last_price < high and self.sell_trigger:
            order = Order(SELL, MARKET, None)
            self.buy_price = None
            self.sell_trigger = False
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