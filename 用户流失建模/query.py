import cx_Oracle
import threading

class DB_Query():
    __query_list = []
    def __init__(self):
        self.connection=cx_Oracle.connect("*","*","*")
        self.cursor = self.connection.cursor()        
        query_1 = """
            select  NVL(sum(ODD_MONEY+EVEN_MONEY)/100,0) balance
            from CBSS_UCR_crm.tf_f_user@ngbil_link a join cbssa1_ucr_act3.TF_F_ACCOUNTDEPOSIT@NGBSS_LINK b on a.user_id=b.user_id
            where END_CYCLE_ID>=to_char(sysdate,'yyyymm') and 
                a.remove_tag=0 and 
                a.serial_number = '%s' 
                group by a.serial_number
            """   
        query_2 = """
            select nvl(FEE/100,0) fee,nvl(sms_count,0)sms_count,nvl(round(FLOW_DATA/1024/1024,2),0) flow_data,
            ceil(nvl(CALL_DURATION,0)/60) call_duration
            from v_4g_realtime_m@local_link where serial_number= '%s' and deal_date=to_number(to_char(add_months(trunc(sysdate),-1),'yyyymm'))
        """
        query_3 = """
            select nvl(FEE/100,0) fee,nvl(sms_count,0)sms_count,nvl(round(FLOW_DATA/1024/1024,2),0) flow_data,
            ceil(nvl(CALL_DURATION,0)/60) call_duration
            from v_3g_realtime_m@local_link where serial_number= '%s' and deal_date=to_number(to_char(add_months(trunc(sysdate),-1),'yyyymm'))
        """
        query_4 = """
            select (case when is_group=4 then 1 else 2 end)
            from t_month_mobile where serial_number='%s' and deal_date=to_number(to_char(add_months(trunc(sysdate),-1),'yyyymm'))
        """
        query_5 = """
            select  nvl(last_deposit_fee,0)last_deposit_fee,nvl(deposit_interval_day,0) from (
            select serial_number,NVL(recv_fee/100,0) as last_deposit_fee,NVL(floor(sysdate-recv_time),999) deposit_interval_day,row_number() over(partition by serial_number order by recv_time desc)rn
            from  TF_B_PAYLOG
            where PAY_FEE_MODE_CODE <>4 and payment_op=16000 and recv_fee>0 and serial_number='%s') where rn=1
        """
        query_6 = """
            select (case when length(pspt_id)=18 then trunc(months_between(sysdate,to_date(substr(pspt_id,7,8),'yyyymmdd'))/12)
            when length(pspt_id)=15 then trunc(months_between(sysdate,to_date('19'||substr(pspt_id,7,6),'yyyymmdd'))/12)
            else 0 end)age
            from cbssc1_ucr_crm3.tf_f_customer@ngbss_link a ,cbssc1_ucr_crm3.tf_f_user@ngbss_link b
            where a.cust_id=b.cust_id and b.serial_number='%s'
        """
        self.__query_list.append(query_1)
        self.__query_list.append(query_2)
        self.__query_list.append(query_3)
        self.__query_list.append(query_4)
        self.__query_list.append(query_5)
        self.__query_list.append(query_6)

    def query(self,number):
        if self.is_tencent_number(number) == 1:
            try:
                balance = self.cursor.execute(self.__query_list[0]%number).fetchmany(1)[0][0]
            except:
                print('获取余额失败')
            # print(balance)
            try:
                query_2 = self.cursor.execute(self.__query_list[1]%number).fetchmany(1)[0]
            except:
                print('获取上月通信消费清单失败')
            # print(query_2)
            fee = query_2[0]
            sms_count = query_2[1]
            flow_data = query_2[2]
            call_duration = query_2[3]
            try:
                develop_type = self.cursor.execute(self.__query_list[3]%number).fetchmany(1)[0][0]
            except:
                pass
            # print(develop_type)
            try:
                query_5 = self.cursor.execute(self.__query_list[4]%number).fetchmany(1)[0]
            except:
                pass
            # print(query_5)
            last_deposit_fee = query_5[0]
            deposit_interval_day = query_5[1]
            try:    
                age = self.cursor.execute(self.__query_list[5]%number).fetchmany(1)[0][0]
            except:
                pass
            # print(age)
            query_rst = [balance,fee,sms_count,flow_data,call_duration,develop_type,last_deposit_fee,age,deposit_interval_day]
            # print(query_rst)
            return query_rst
        else:
            print('用户手机套餐非大王卡套餐，请输入大王卡用户号码')
    #查询当前余额
    def balance_query(self,number):
        try:
            balance = self.cursor.execute(self.__query_list[0]%number).fetchmany(1)[0][0]
            if balance == None:
                return 0
            else:
                return balance
        except:
            print('获取余额失败')
        # print(self.balance)
    #查询上月通信消费情况
    def expenses_query(self,number):
        try:
            expenses = self.cursor.execute(self.__query_list[1]%number).fetchmany(1)[0]
            return expenses
        except:
            print('获取上月通信消费清单失败')
        # print(expenses)
    #查询发展渠道
    def develop_type_query(self,number):
        try:
            develop_type = self.cursor.execute(self.__query_list[3]%number).fetchmany(1)[0][0]
        except:
            pass
        # print(develop_type)
        return develop_type
    #查询充值情况
    def deposit_query(self,number):
        try:
            query_5 = self.cursor.execute(self.__query_list[4]%number).fetchmany(1)[0]
        except:
            pass
        # print(query_5)
        last_deposit_fee = query_5[0]
        deposit_interval_day = query_5[1]
        return (last_deposit_fee,deposit_interval_day)
    #查询年龄
    def age_query(self,number):
        try:    
            age = self.cursor.execute(self.__query_list[5]%number).fetchmany(1)[0][0]
        except:
            pass
        # print(age)
        return age
    #判断是否是套餐大王卡
    def is_tencent_number(self,number):
        # print(threading.current_thread().name)
        query = "select (case when product_id='90063345' then 1 else 0 end) from v_day_realtime where serial_number='{}'".format(number)
        try:
            result = self.cursor.execute(query).fetchmany(1)[0][0]
            # print(result)
            if result == 1:
                return 1
            else:
                return 0
        except:
            return 0
    #查询号码是否在网状态
    def is_destory(self,number):
        return 1


if __name__ == '__main__':
    dbq = DB_Query()
    # dbq.query('18666919990')
    # dbq.age_query('18666919990')
    print(dbq.develop_type_query('18666919990'))