# -*- encoding: UTF-8 -*-

import utils
import logging
import work_flow
import settings
import schedule
import time
from datetime import datetime 
from pathlib import Path
from buyAndSell.MA_Cross import MA_Cross, get_data
import backtrader as bt


def job():
    if utils.is_weekday():
        work_flow.prepare()

# 创建logs目录
Path('logs').mkdir(exist_ok=True)

current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_filename = f'logs/sequoia_{current_time}.log'
logging.basicConfig(format='%(asctime)s %(message)s', filename=log_filename)
logging.getLogger().setLevel(logging.INFO)
settings.init()

if settings.config['cron']:
    EXEC_TIME = "15:15"
    schedule.every().day.at(EXEC_TIME).do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
elif settings.config['self']: 
    EXEC_TIME = "15:15"
    work_flow.prepare(True)
elif settings.config['back']: 
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
    cerebro.broker.setcash(100000)  # 设置初始资金10万
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
else:
    work_flow.prepare()
