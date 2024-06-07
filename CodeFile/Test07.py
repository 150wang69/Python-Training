import pymysql
import xlrd
import pandas as pd


#打开工作表
#wb = xlrd.open_workbook("score.xlsx")
# ws = wb.sheet_by_name("Sheet")
# wb = openpyxl.load_workbook("score.xlsx")
# ws = wb["Sheet"]

#连接数据库
connect = pymysql.Connect(
    host="localhost", #主机名
    port =3306, #端口号
    user = "root", #数据库用户名
    passwd = "wy200469", #密码
    db = "school", #数据库名称
    charset = "utf8" #编码格式
)

#获取游标
cursor = connect.cursor()
#执行SQL查询
# cursor.execute("SELECT VERSION()")
# #获取单条数据
# version = cursor.fetchone()
# #打印输出
# print("MySQL数据库的版本是:%s" % version)
#关闭数据库的连接
#connect.close()

# #若表存在，删除
# cursor.execute("DROP TABLE IF EXISTS score")
# #设定SQL语句
# sql = """
# CREATE TABLE score(
#
# )"""

df = pd.read_excel("score.xlsx") #使用pandas读取Excel表格的内容
cursor.execute("DROP TABLE IF EXISTS score")
sql = """
CREATE TABLE score(
语文 int,
数学 int,
英语 int);
"""

cursor.execute(sql)
for index,row in df.iterrows():
    sql = 'INSERT INTO score(语文,数学,英语) VALUES(%s,%s,%s)'
    cursor.execute(sql,tuple(row))
connect.commit()
connect.close()
print("导入成功！")
# query = "insert into score (语文,数学,英语) values (%s,%s,%s)"
# # 创建一个for循环读取表格中的每一行数据，从第二行开始。
# # for i in range(1,ws.nrows):
# #     语文 = ws.cell(i,0).value
# #     数学 = ws.cell(i,1).value
# #     英语 = ws.cell(i,2).value
# #     values = (语文,数学,英语)
# for row in ws.iter_rows(min_row=2, values_only=True):
#     语文, 数学, 英语 = row
#     values = (语文, 数学, 英语)
#     # 执行 SQL 语句
#     cursor.execute(query, values)
#     #执行sql语句
#     cursor.execute(query,values)
#
# connect.commit()
# cursor.close()
# connect.close()
#
# # columns = str(ws.ncols)
# # rows = str(ws.nrows)
# # print("导入" + columns + "列" + rows + "行数据到MySQL数据库")
# rows = ws.max_row - 1
# print(f"导入{rows}行数据到MySQL数据库")



