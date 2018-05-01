import threading
import time
from query import DB_Query
import pandas as pd
class MyThread(threading.Thread):
    def __init__(self,func,args=()):
        super(MyThread,self).__init__()
        self.func = func
        self.args = args
    def run(self):
        self.result =  self.func(*self.args)
    #获取查询结果    
    def get_result(self):
        try:
            return self.result 
        except Exception as e:
            return e
if __name__ == '__main__':
    q1 = DB_Query()
    q2 = DB_Query()
    #余额查询
    t1 =  MyThread(q1.balance_query,args=('18666919990',))
    #通信消费查询
    t2 =  MyThread(q2.expenses_query,args=('18666919990',))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    balance = t1.get_result()
    fee,sms_count,flow_data,call_duration = t2.get_result()
    print(balance,fee,sms_count,flow_data,call_duration)

