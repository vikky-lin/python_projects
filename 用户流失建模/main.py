from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter.filedialog as dir
from sklearn.externals import joblib
import numpy as np
import xlrd
import xlwt
import pandas as pd
import cx_Oracle 
import re
import threading
from query import DB_Query
from my_thread import MyThread
import os

class AppUI():

    def __init__(self):
        root = Tk()
        self.create_menu(root)  
        self.create_content(root)
        # self.path = 'D:'
        self.clf = None #模型
        self.model_state = None #模型加载状态
        self.current_list = set()  #保存当前号码清单
        self.predict_result = []    #保存预测结果
        root.title("腾讯王卡用户流失预测")
        root.update()
        curWidth = root.winfo_width()  
        curHeight = root.winfo_height()  
        scnWidth, scnHeight = root.maxsize()  
        tmpcnf = '+%d+%d' % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        root.geometry(tmpcnf)
        root.mainloop()


    def create_menu(self,root):
        #创建菜单栏
        menu = Menu(root)
        file_menu = Menu(menu,tearoff=0)
        menu.add_command(label="批量导入",command=self.load_file)
        menu.add_command(label="加载模型",command=self.load_model)
        root['menu'] = menu

    def create_content(self, root):
        lf = ttk.LabelFrame(root, text="")
        lf.pack(fill=X, padx=20, pady=8)
        #号码输入窗口
        top_frame = Frame(lf)
        top_frame.pack(fill=X,expand=YES,side=TOP,padx=15,pady=8)
        self.input_entry = ttk.Entry(top_frame,width=50)
        self.input_entry.pack(fill=X,expand=YES,side=LEFT)
        ttk.Button(top_frame,text="添加号码",command=self.add_number).pack(padx=15,fill=X,expand=YES)
        #测试窗口
        test_frame = LabelFrame(lf,text='测试窗口')
        test_frame.pack(fill=BOTH,expand=YES,side=TOP,padx=15,pady=8)
        balance_frame = LabelFrame(test_frame,text='balance')
        balance_frame.pack(fill=BOTH,expand=YES,side=LEFT)
        self.balance = ttk.Entry(balance_frame, textvariable='balance')
        self.balance.pack(fill=X,expand=YES,side=LEFT)
        fee_frame = LabelFrame(test_frame,text='fee')
        fee_frame.pack(fill=BOTH,expand=YES,side=LEFT)
        self.fee = ttk.Entry(fee_frame, textvariable='fee')
        self.fee.pack(fill=X,expand=YES,side=LEFT)
        sms_count_frame = LabelFrame(test_frame,text='sms_count')
        sms_count_frame.pack(fill=BOTH,expand=YES,side=LEFT)
        self.sms_count = ttk.Entry(sms_count_frame, textvariable='sms_count')
        self.sms_count.pack(fill=X,expand=YES,side=LEFT)
        flow_data_frame = LabelFrame(test_frame,text='flow_data')
        flow_data_frame.pack(fill=BOTH,expand=YES,side=LEFT)
        self.flow_data = ttk.Entry(flow_data_frame, textvariable='flow_data')
        self.flow_data.pack(fill=X,expand=YES,side=LEFT)
        call_duration_frame = LabelFrame(test_frame,text='call_duration')
        call_duration_frame.pack(fill=BOTH,expand=YES,side=LEFT)
        self.call_duration = ttk.Entry(call_duration_frame, textvariable='call_duration')
        self.call_duration.pack(fill=X,expand=YES,side=LEFT)
        develop_type_frame = LabelFrame(test_frame,text='develop_type')
        develop_type_frame.pack(fill=BOTH,expand=YES,side=LEFT)
        self.develop_type = ttk.Entry(develop_type_frame, textvariable='develop_type')
        self.develop_type.pack(fill=X,expand=YES,side=LEFT)
        last_deposit_fee_frame = LabelFrame(test_frame,text='last_deposit_fee')
        last_deposit_fee_frame.pack(fill=BOTH,expand=YES,side=LEFT)
        self.last_deposit_fee = ttk.Entry(last_deposit_fee_frame, textvariable='last_deposit_fee')
        self.last_deposit_fee.pack(fill=X,expand=YES,side=LEFT)
        age_frame = LabelFrame(test_frame,text='age')
        age_frame.pack(fill=BOTH,expand=YES,side=LEFT)
        self.age = ttk.Entry(age_frame, textvariable='age')
        self.age.pack(fill=X,expand=YES,side=LEFT)
        deposit_interval_day_frame = LabelFrame(test_frame,text='deposit_interval_day')
        deposit_interval_day_frame.pack(fill=BOTH,expand=YES,side=LEFT)
        self.deposit_interval_day = ttk.Entry(deposit_interval_day_frame, textvariable='deposit_interval_day')
        self.deposit_interval_day.pack(fill=X,expand=YES,side=LEFT)

        bottom_frame = Frame(lf)
        bottom_frame.pack(fill=BOTH,expand=YES,side=TOP,padx=15,pady=8)
        #号码清单窗口
        left_frame = LabelFrame(bottom_frame,text=' 号码清单 ',width=20)
        left_frame.pack(fill=BOTH,expand=YES,side=LEFT)       
        self.number_list = Text(left_frame,width=20,font =("微软雅黑", 12,"bold"))
        self.number_list.pack(side=TOP,fill=BOTH,expand=YES)
        #预测窗口
        pred_frame = LabelFrame(bottom_frame,relief=FLAT)
        pred_frame.pack(side=LEFT)
        #预测按钮         
        ttk.Button(pred_frame,text=">>预测>>",command=self.input_predict).pack(pady=5,expand=0,side=TOP)
        ttk.Button(pred_frame,text=">>test>>",command=self.data_predict).pack(pady=5,expand=0,side=TOP)
        ttk.Button(pred_frame,text="清空",command=self.clear).pack(padx=5,expand=0,side=BOTTOM)
        #预测窗口
        right_frame = LabelFrame(bottom_frame,text=' 预测结果 ',width=50)
        right_frame.pack(fill=BOTH,expand=YES,side=LEFT)     
        self.result = Text(right_frame,width=50,font =("微软雅黑", 12,"bold"))
        self.result.pack(side=TOP,fill=BOTH,expand=YES)
        ttk.Button(right_frame,text="导出",command=self.save_result).pack(padx=5,expand=0,side=TOP)
        #消息窗口
        msg_frame = LabelFrame(bottom_frame,text=' 消息窗口 ',width=40)
        msg_frame.pack(fill=BOTH,expand=YES,side=LEFT)     
        self.msg = Text(msg_frame,width=40)
        self.msg.pack(side=TOP,fill=BOTH,expand=YES)
    
    def add_number(self):
        error_list = ''
        # self.current_list = self.current_list|set(self.number_list.get('1.0',END).split())
        for number in list(map(str.strip,self.input_entry.get().split(','))):
            if number == '':
                pass
            elif self.is_number(number):
                if number not in self.current_list:
                    self.number_list.insert(END,number+'\n')
                    self.current_list.add(number)
                else:
                    messagebox.showwarning('提示','号码已存在:\n%s'%number)
            else:
                error_list +=number+'\n'
        if len(error_list)>0:
            messagebox.showwarning('提示','以下号码输入格式有误:\n%s'%error_list)
        self.input_entry.delete(0,END)

    #清空所有内容
    def clear(self):
        self.number_list.delete(1.0,END)
        self.current_list = set()
        self.predict_result = []
        self.result.delete(1.0,END)
        self.msg.delete(1.0,END)

    #用于测试数据
    def data_predict(self):
        self.result.delete(1.0,END)
        self.msg.delete(1.0,END)
        lost_cnt = 0
        invalid_cnt = 0
        if self.clf != None:
            for number in self.current_list:
                self.msg.insert(END,'加载 %s 数据...\n'%number)
                test_data = pd.DataFrame([[float(self.balance.get()),
                                            float(self.fee.get()),
                                            float(self.sms_count.get()),
                                            float(self.flow_data.get()),
                                            float(self.call_duration.get()),
                                            float(self.develop_type.get()),
                                            float(self.last_deposit_fee.get()),
                                            float(self.age.get()),
                                            float(self.deposit_interval_day.get())]])
                print(self.clf.predict(test_data)[0])
                try:
                    self.msg.insert(END,'    >>>正在预测...\n')
                    if self.clf.predict(test_data)[0] == 0:
                        self.result.insert(END,'%s   >>>    否\n'%number)
                    else:
                        self.result.insert(END,'%s   >>>    是\n'%number)
                        lost_cnt += 1
                    self.msg.insert(END,'    >>>预测结果已输出...\n')
                except Exception as e:
                    self.msg.insert(END,'    >>>获取 %s 数据失败\n'%number)
            self.msg.insert(END,'********************************\n运行结果：号码总数%s个，无效号码%s个，预测流失%s个\n'%(len(self.current_list),invalid_cnt,lost_cnt))
        else:
            messagebox.showwarning('提示','模型尚未加载，请先加载模型')

    #号码流失预测
    def input_predict(self):
        self.result.delete(1.0,END)
        self.msg.delete(1.0,END)
        lost_cnt = 0
        invalid_cnt = 0
        # print(self.current_list)
        if self.clf != None:
            for number in self.current_list:
                q = DB_Query()
                self.msg.insert(END,'读取 %s 数据...\n'%number)
                self.msg.update()
                if q.is_tencent_number(number) == 0: #or q.is_destory(number) == 1:
                    self.msg.insert(END,'    >>>无效号码\n')
                    invalid_cnt += 1
                    self.msg.update()
                    continue
                else:
                    try:
                        self.msg.insert(END,'    >>>正在计算...\n')
                        self.msg.update()
                        # print(self.search_from_database(number))
                        input_data = pd.DataFrame([self.search_from_database(number)])
                        if self.clf.predict(input_data)[0] == 0:
                            self.result.insert(END,'%s   >>>    否\n'%number)
                            self.predict_result.append([number,'否'])
                        else:
                            self.result.insert(END,'%s   >>>    是\n'%number)
                            self.predict_result.append([number,'是'])
                            lost_cnt += 1
                        self.msg.insert(END,'    >>>预测结果已输出...\n')
                        self.msg.update()
                    except Exception as e:
                        self.msg.insert(END,'    >>>获取%s数据失败\n'%number)
            self.msg.insert(END,'********************************\n运行结果：号码总数%s个，无效号码%s个，预测流失%s个\n'%(len(self.current_list),invalid_cnt,lost_cnt))
                
        else:
            messagebox.showwarning('提示','模型尚未加载，请先加载模型')
    def search_from_database(self,number):
        thread_list = []
        q1 = DB_Query()
        q2 = DB_Query()
        q3 = DB_Query()
        q4 = DB_Query()
        q5 = DB_Query()
        #余额查询
        t1 =  MyThread(q1.balance_query,args=(number,))        
        #通信消费查询
        t2 =  MyThread(q2.expenses_query,args=(number,))
        #发展渠道
        t3 =  MyThread(q3.develop_type_query,args=(number,))
        #充值查询
        t4 =  MyThread(q4.deposit_query,args=(number,))
        #年龄查询
        t5 =  MyThread(q5.age_query,args=(number,))
        thread_list = [t1,t2,t3,t4,t5]
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()
        balance = t1.get_result()
        fee,sms_count,flow_data,call_duration = t2.get_result()
        develop_type = t3.get_result()
        last_deposit_fee,deposit_interval_day = t4.get_result()
        age = t5.get_result()
        return [balance,fee,sms_count,flow_data,call_duration,develop_type,last_deposit_fee,age,deposit_interval_day]

    #获取文件类型
    def get_filetype(self,file_path):
        suffix = file_path.split('.')[-1]
        if suffix == 'txt':
            return 'text'
        elif suffix == 'xlsx':
            return 'excel'
        elif suffix == 'csv':
            return 'csv'
        elif len(suffix)== 0:
            return None
        else:
            return 0

    #批量导入号码
    def load_file(self):
        self.current_list = set()
        self.number_list.delete(1.0,END)
        file_path = dir.askopenfilename()
        file_type = None
        file_type = self.get_filetype(file_path)
        dataMat = []
        if file_type == None:
            pass
        elif file_type == 'text':
            fr = open(file_path)
            for number in fr.readlines():
                # dataMat.append([float(lineArr[0]),float(lineArr[1])])
                if self.is_number(number):
                    self.number_list.insert(END,number.strip()+'\n')
                    self.current_list.add(number.strip())
            file_type = None
            # print(self.current_list)
        elif file_type == 'excel':
            data = xlrd.open_workbook(file_path)
            table = data.sheets()[0]
            dataMat = table.col_values(0)
            for number in dataMat:
                number = str(number).strip('.0')
                if self.is_number(number):
                    self.number_list.insert(END,number+'\n')
                    self.current_list.add(number.strip())
            file_type = None
        else:
            messagebox.showerror('错误','文件格式错误，请重新选择导入文件!')
            file_type = None

    #加载训练好的模型
    def load_model(self):
        file_path = dir.askopenfilename()
        # file_path = './model/gdbt_model.m'
        try:
            self.clf = joblib.load(file_path)
            messagebox.showinfo('提示','模型已加载:\n%s'%self.clf)
            self.model_state = 1
        except Exception as e:
            messagebox.showinfo('提示',e)
            # print(e)

    #判断输入号码是否合法
    def is_number(self,number):
        pattern = re.compile('^1([358][0-9]|4[579]|66|7[0135678]|9[89])[0-9]{8}$')
        error_list = ''
        if pattern.match(number):
            return True
        else:
            return False
            
    #导出预测结果
    def save_result(self):
        if len(self.predict_result) == 0:
             messagebox.showwarning('提示','列表为空,不能导出')
        else:
            file_path = dir.askdirectory()
            workbook = xlwt.Workbook(encoding = 'utf-8')
            worksheet = workbook.add_sheet('预测结果')
            # 写入excel
            worksheet.write(0,0, label = '号码')
            worksheet.write(0,1, label = '是否流失')
            for index,item in enumerate(self.predict_result,1):
                worksheet.write(index,0,label = item[0])
                worksheet.write(index,1,label = item[1])
            # 保存
            if file_path != '':
                try:
                    workbook.save('%s/预测结果.xls'%file_path)
                except:
                    messagebox.showwarning('提示','导出失败')
                messagebox.showinfo('提示','导出成功!')

if __name__ == "__main__":
    AppUI()
