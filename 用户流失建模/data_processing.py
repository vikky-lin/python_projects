import numpy as np
import pandas as pd
from datetime import datetime

data = pd.read_csv('./data/tencent_traindata.csv')
# print(data.head(5))
data = data[['SERIAL_NUMBER','USER_STATE_CODESET','BALANCE','FEE','SMS_COUNT','FLOW_DATA','CALL_DURATION','PSPT_ID','DEVELOP_TYPE','LAST_DEPOSIT_FEE','LAST_DEPOSIT_TIME']]
data.BALANCE = data.BALANCE.fillna(0)

#设置样本标签
def set_type(USER_STATE_CODESET):
    if USER_STATE_CODESET == '0':
        return 0
    else:
        return 1
data['class'] = data.USER_STATE_CODESET.apply(set_type)

#获取年龄
def get_birth(pspt_id):
    if len(pspt_id) == 18:
        print(datetime(int(pspt_id[6:10]),int(pspt_id[10:12]),int(pspt_id[12:14])))
        return int(((datetime.now()-datetime(int(pspt_id[6:10]),int(pspt_id[10:12]),int(pspt_id[12:14]))).days)/365)
    else:
        return int(((datetime.now()-datetime(int('19'+pspt_id[6:8]),int(pspt_id[8:10]),int(pspt_id[10:12]))).days)/365)
data['age'] = data.PSPT_ID.apply(get_birth)

#获取充值时间间隔天数
def get_interval(last_deposit_time):
    return (datetime(2018,4,8)-last_deposit_time).days
data['deposit_interval_day'] = data.LAST_DEPOSIT_TIME.apply(get_interval)
data.LAST_DEPOSIT_TIME = pd.to_datetime(data.LAST_DEPOSIT_TIME)
data1 = data[['BALANCE','FEE','SMS_COUNT','FLOW_DATA','CALL_DURATION','DEVELOP_TYPE','LAST_DEPOSIT_FEE','age','deposit_interval_day','class']]
data1.to_csv('./data/training_data1.csv',index=None)