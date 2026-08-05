import pandas as pd 
from sqlalchemy import create_engine
import pymysql
import config.settings as config

#连接数据库，批量入库
def csv_to_sql(csv_file,table_name):
    try:
        #读取csv文件，mysql自动匹配编码，处理空值
        df = pd.read_csv(csv_file,encoding="utf-8-sig",na_values=["","NaN"],engine="python")
        print(f"成功读取文件{csv_file},数据行数：{len(df)}")

        #创建数据库连接引擎
        engine = create_engine(
            f"mysql+pymysql://{config.mysql_config['user']}:{config.mysql_config['password']}@{config.mysql_config['host']}:{config.mysql_config['port']}/{config.mysql_config['db']}?charset={config.mysql_config['charset']}"
        )
        """
        mysql连接url的固定格式，通用：
        数据库类型+驱动://用户名:密码@主机地址:端口/数据库名?参数1=值1&参数2=值2
        """

        #写入mysql，表不存在自动创建，存在则覆盖，避免重复数据
        df.to_sql(
            name = table_name,
            con = engine,
            if_exists = "replace", #存在则覆盖
            index = False, #不存入pandas所银行，避免冗余
            chunksize = 1000 #分批入库，防止数据量大时超时
        )
        print(f"成功入库，数据表：{config.mysql_config['db']}:{table_name}\n")

    except Exception as e:
        print(f"处理失败：原因{e}")