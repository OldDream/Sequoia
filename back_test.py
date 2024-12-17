from datetime import datetime
import backtrader as bt
from buyAndSell.MA_Cross import MA_Cross, get_data


def run_back_test():
    start = datetime(2024, 1, 1)
    end = datetime(2024, 12, 16)
    
    # 创建回测引擎
    cerebro = bt.Cerebro()
    
    # 读取股票数据
    with open('myStocks.txt', 'r', encoding='utf-8') as f:
        for line in f:
            parts = [part.strip() for part in line.strip().split('\t')]
            if len(parts) >= 2:
                code = parts[0]
                name = parts[1]
                # 获取数据并添加到回测引擎
                dataframe = get_data(code, start=start.strftime('%Y%m%d'), end=end.strftime('%Y%m%d'))
                data = bt.feeds.PandasData(dataname=dataframe, fromdate=start, todate=end)
                cerebro.adddata(data, name=f"{code}_{name}")
    
    # 设置初始资金和手续费
    cerebro.broker.setcash(10000)  # 设置初始资金1万
    cerebro.broker.setcommission(commission=0.0005)  # 设置手续费为0.05%
    
    # 添加策略
    cerebro.addstrategy(MA_Cross)
    
    # 打印初始资金
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    # 运行回测
    cerebro.run()
    
    # 打印最终资金
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    # 绘制结果
    cerebro.plot() 