from datetime import datetime

import numpy as np
import pandas as pd
import akshare as ak
import backtrader as bt


class MA_Cross(bt.Strategy):
    params = (
        ('pfast', 5),  # period for the fast moving average
        ('pslow', 10),   # period for the slow moving average
    )

    def log(self, txt, dt=None):
        """Logging function fot this strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        print("%s, %s" % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.volume = self.datas[0].volume
        self.order = None
        self.buyprice = None
        self.buycomm = None

        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal

    def next(self):
        self.log("Close, %.2f" % self.dataclose[0])

        # 未持有
        if self.position.size == 0:
            if self.crossover > 0:  # 金叉
                self.log("BUY CREATE, %.2f" % self.dataclose[0])
                self.size = np.floor(0.95 * self.broker.cash / self.dataclose[0])
                self.buy(size=self.size)
        # 已持有
        elif self.position.size > 0:
            if self.crossover < 0:  # 死叉
                self.log("SELL CREATE, %.2f" % self.dataclose[0])
                self.sell(size=self.position.size)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.bar_executed_close = self.dataclose[0]
            else:
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm))

def get_data(code, start="20240801", end="20240930"):
    # 将股票代码转换为正确的格式
    if code.isdigit():
        if code.startswith('6'):
            symbol = f"{code}"
        else:
            symbol = f"{code}"
    
    # 使用akshare获取数据
    print('symbol',symbol,start,end)
    df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start, end_date=end, adjust="qfq")
    print(df)
    # 重命名列以匹配backtrader要求
    df = df.rename(columns={
        '日期': 'date',
        '开盘': 'open',
        '最高': 'high',
        '最低': 'low',
        '收盘': 'close',
        '成交量': 'volume'
    })
    
    # 设置日期索引
    df.index = pd.to_datetime(df.date)
    df["openinterest"] = 0
    df = df[["open", "high", "low", "close", "volume", "openinterest"]]
    return df

if __name__ == "__main__":

    start = datetime(2024, 1, 1)
    end = datetime(2024, 12, 16)
    dataframe = get_data("601038", start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
    data = bt.feeds.PandasData(dataname=dataframe, fromdate=start, todate=end)

    cerebro = bt.Cerebro()

    cerebro.addstrategy(MA_Cross)

    cerebro.adddata(data)

    cerebro.broker.setcash(10000)

    cerebro.broker.setcommission(commission=0.0005)

    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    cerebro.run()

    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())

    cerebro.plot()
