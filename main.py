# -*- encoding: UTF-8 -*-

import utils
import logging
import work_flow
import settings
import schedule
import time
from datetime import datetime 
from pathlib import Path
from back_test import run_back_test


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
    run_back_test()
else:
    work_flow.prepare()
