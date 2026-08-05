import pandas as pd
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
codes_dir = os.path.dirname(current_dir)
sys.path.append(codes_dir)
from mysql.sql_connect import csv_to_sql

def check_files_exists(dataset_dir,file_total,file_longevity,files_to_merge):
    #所有文件一起检查
    all_files = []
    all_files.extend(files_to_merge)
    all_files.append(file_longevity)
    all_files.append(file_total)
    #存储丢失文件
    missing_files = []

    #检查文件是否存在
    print("==========================================")
    print("正在核对文件是否存在")

    for file_name in all_files:
        file_path = os.path.join(dataset_dir,file_name)  #完整文件名

        if os.path.exists(file_path):
            # print(f"文件{file_name}存在")
            continue
        else:
            missing_files.append(file_path)
            print(f"文件{file_name}不存在")

    #输出不存在的文件
    if not missing_files:
        print("==========================================")
        print("所有文件都存在，检查完成")

"""
该方法使用传统的文件读取方式with open()逐行读取文件，获取列名
对比两种方法，效率无明显差别
且该方法适用性更强
"""
#合并14个结构一致的文件
def merge_files(files,out_file="merge_data.csv"):
    print("计划合并以下文件：")                     
    for i,file_name in enumerate(files,1):
        print(f"{i}.{file_name}")

    all_data = [] #存储处理完的文件df

    for file in files:
        print("=======================================================")
        print(f"正在处理文件{file}")
        # file_name = os.path.basename(file)
                
        df_melted = None #初始化，找到表头后直接设置表头行
        
        df_melted = get_col(file) #获取列名和表头，得到df

        all_data.append(df_melted)

    #此处判断逻辑同废弃掉的方法
    #先检查是否有处理好的数据
    if all_data:
        print("===========================================")
        print(f"成功处理了{len(all_data)}个文件，准备合并")
    else:
        print("===========================================")
        print("没有成功处理任何文件，无法进行合并")
        return None
    
    #合并数据
    print("===========================================")
    print("开始合并数据")
    from functools import reduce
    
    #按照地区和年份进行外连接合并
    merged =reduce(lambda left,right:pd.merge(left,right,on=["地区","年份"],how="outer"),all_data) 
    # #过滤掉最后的注释行，只保留地区和年份不为空行
    # merged = merged.dropna(subset=["地区","年份"])
    print(f"\n所有文件合并完成，共{merged.shape[0]}行 * {merged.shape[1]}列数据")

    #保存合并文件为.csv
    save_csv(merged,"merged_data.csv")

    return merged

#清洗数据，获取列名、表头，长格式转换
def get_col(file):
    path = os.path.join(dataset_dir,file)
    with open(path,"r",encoding="gbk") as f:
        #去掉换行和空格
        all_lines = [line.strip() for line in f.readlines() if line.strip()]
        # print(all_lines[:5]) #输出前五行，检查是否正确读取文件

    indicator_name = None #初始化列名
    df = None #初始化，找到表头后直接设置表头行

    #筛选表头行，获取指标列名
    for idx,line in enumerate(all_lines):
        try:
            #按照逗号拆分列，过滤掉空列。（此处修复前方法中的逗号分割符不统一）
            cols = [col.strip() for col in line.split(",") if col.strip()]

            if df is None:
                #df为空说明均未获取，遍历列数据
                # print(f"第{idx+1}行，cols={cols}")
                try:
                    #如果列名未获取，且找到指标行则获取。
                    if indicator_name is None and "指标" in cols[0]: 
                        #由于循环外col.strip缺少了一个(),报错TypeError: argument of type 'builtin_function_or_method' is not iterable
                        indicator_name = cols[0].replace("指标：","").replace(",","").strip()
                        print(f"成功获取指标列名：{indicator_name}")
                    #如果已经获取列名，且找到第一个列名是地区，则为表头行。
                    #此处也可以增加一个年份列数据的判断。
                    if indicator_name is not None and cols[0] == "地区":
                        print(f"找到表头，{cols}") #检验是否正确
                        #定义df
                        df = pd.read_csv(path,encoding="gbk",skiprows=idx,engine="python",sep=",") #跳过表头行之前的行，直接设置表头行
                        print(f"成功找到第{idx+1}行是表头行")
                        # print(df) #此处还是有最后两行的脏数据
                    # else:
                    #     print(f"列名{indicator_name}和表头{df}获取失败")
                
                except Exception as e:
                    print(f"获取指标列名失败，失败原因：{e}")
            
            elif df is not None and indicator_name is not None:
                #已经找到列名和表头了，结束循环
                break
        
        except Exception as e:
            print(f"文件处理错误：{e}")

    # df和列名均获取
    # 将表转化为长格式
    # id_vars表示不改变的列，var_name表示其余列全都改变为一列，新列的列名，value_name表示新列的值的列名
    df_melted = pd.melt(df,id_vars=["地区"],var_name="年份",value_name=indicator_name)
    
    # # 清洗掉最后两行的注释部分（根据年份列是否为空判断）
    df_melted = df_melted.dropna(subset=[indicator_name]) 
    # # 此处前逻辑为“年份”判断空，但实际上年份有数据，指标无数据，所以应该用指标清洗
    # # print(df_melted) #检查转化是否正确

    return df_melted

#清洗后的数据另存为.csv
def save_csv(df,save_name):
    path = "论文\output"
    save_name = os.path.join(path,save_name)
    if df is not None:
        df.to_csv(save_name,index=False,encoding="utf-8-sig")
        print(f"合并数据已保存为{save_name}")

#其余两个文件不需要合并，只需要清洗数据
#清洗预期寿命.csv
def clear_longevity(file,out_file="longevity.csv"):
    df_melted = None

    df_melted = get_col(file) #相同的框架，完成长格式转换

    save_csv(df_melted,out_file)

#清洗卫生总费用.csv
#清洗规则不同，需要重写清洗逻辑
def clear_total(file,out_file="total_cost.csv"):
    path = os.path.join(dataset_dir,file)
    df = None

    with open(path,"r",encoding="gbk") as f:
        #去掉换行和空格
        all_lines = [line.strip() for line in f.readlines() if line.strip()]
        # print(all_lines[:5]) #输出前五行，检查是否正确读取文件
    
    for idx,line in enumerate(all_lines):
        cols = [col.strip() for col in line.split(",") if col.strip()]

        if cols[0] == "指标":
            df = pd.read_csv(path,encoding="gbk",skiprows=idx,engine="python",sep=",") #跳过表头行之前的行，直接设置表头行
            
            df = df.iloc[:-5] #保留倒数3行之前的数据，即清除掉了前后的注释行
            """因为是对单表进行处理，才这么做。如果是多表还是要用通用处理方法。"""
            break

    # print(df)

    #将第一列设置为索引，并重命名索引为年份
    df = df.rename(columns={"指标":"年份"})
    # print(df)
    df = df.set_index("年份")
    #行列转置
    df_wide = df.T.reset_index()
    df_wide = df_wide.rename(columns={"index":"年份"})
    # print(df_wide)
    
    save_csv(df_wide,out_file)

if __name__ == "__main__":

    #初始化文件
    dataset_dir = "论文\dataset" #文件路径的前缀，搜索时添加
    file_total = "全国各项卫生总支出.csv" #单独文件，作为宏观数据分析的背景，也可以与合并的大表对指标进行衍生计算
    file_longevity = "预期寿命.csv" 
    files_to_merge = ["出生率.csv","各地区教育支出.csv","各地区居民人均消费支出.csv","各地区生产总值.csv",
                    "各地区生产总值指数.csv","各地区医疗卫生机构床位数.csv","各地区医疗卫生机构数.csv",
                    "各地区医疗卫生支出.csv","各地区医院床位使用率.csv","每万人卫生技术人员数.csv",
                    "每万人医疗机构床位数.csv","年末常住人口.csv","人口自然增长率.csv","死亡率.csv"
                    ]
    
    print("########################一、检查##########################")
    check_files_exists(dataset_dir,file_total,file_longevity,files_to_merge)

    print("\n########################二、清洗、合并##########################")
    merged = merge_files(files_to_merge)
    print("=================================")
    clear_longevity(file_longevity)
    print("=================================")
    clear_total(file_total)
    print("\n########################三、数据入库#########################")
    #配置需要入库的csv文件，一共三张csv表
    csv_files = [
        "论文\output\\total_cost.csv",
        "论文\output\\longevity.csv",
        "论文\output\\merged_data.csv"
    ]

    #定义数据表名
    table_names = [
        "total_cost",
        "longevity",
        "merged_data"
    ]
    for csv_file,table_name in zip(csv_files,table_names):
        csv_to_sql(csv_file,table_name)
    
    # merge_files(csv_files)
    # print(merged)




"""
舍弃该方法（pd读取）因为文件的间隔符不同，则指标列名行无法解析，无法正确获取（None）
但可作为参考方法
该方法适用文件前几行格式相同活差别不大的情况（比如前2或3行是注释行，使用skiprow判断方便开销也不大）
"""
# def merge_files(csv_files,output_file="merge_data.csv"):
#     """将多个分省年度数据csv文件合并为一个面板数据格式"""
#     #初始化一个空列表，存储每个文件处理后的数据框
#     all_date = []
#     for file in csv_files:
#         print("===========================================")    
#         print(f"正在处理文件{file}")
#         #获取文件名（不含路径）作为指标名称的参考
#         file_name = os.path.basename(file)

#         #提取指标名称（去掉csv，去掉各地区），此处弃用
#         # indicator_name = file_name.replace("各地区","").replace(".csv","")
#         indicator_name = None

#         #尝试不同的skiprow，找到正确的表头（注意：表头下面是第一行也就是下标为0）
#         df = None #先初始化，不然可能会报错UnboundLocalError: local variable 'df' referenced before assignment
#         for skip_rows in [0,1,2,3]:

#             try:
#                 #尝试不同的skiprows参数，找到正确的表头行数，sep参数指定分隔符为逗号，engine参数指定使用python解析器以处理复杂的csv文件
#                 temp_df = pd.read_csv(file, encoding="gbk", skiprows=skip_rows,engine="python") 
#                 #检查是否为有效数据（14个表中第一列应该包含地区信息，全国卫生总支出表中应该包含指标信息）
#                 first_col = temp_df.columns[0] #第一列的列名（相当于表头）
#                 print(f"skip={skip_rows},first_col={first_col}")
#                 #temp_df[first_col]是第一列的所有数据，.iloc[0]是第一列的第一行数据
#                 #获取指标名字（同时包含单位名称），使文件表的指标一行的数据作为该文件的指标列名，包含单位不需要自己再添加
#                 if "指标" in first_col:
#                     indicator_name = first_col.replace("指标：","").replace(",","").strip() #去掉指标：前缀，并去掉两端的空格
#                     #此处replace是替换掉所有的字符，如果指定替换掉前n个字符，可以加一个count参数，replace(old,new,count)，count指定替换的次数，默认为-1，表示替换所有的old字符串
#                     print(f"成功获取指标列名：{indicator_name}")
                
#                 if indicator_name is None:
#                     print("指标列名获取失败")
                
#                 #判断是否是表头
#                 if any(info in str(temp_df[first_col].iloc[0]) for info in ["北京市","天津市","河北省"]):
#                     print(f"成功读取{file},跳过{skip_rows}行作为表头")
#                     df = temp_df
#                     break

#             except Exception as e:
#                 print(f"skip_row={skip_rows}时读取{file}失败，错误信息：{e}")
#                 continue
        
#         #检查df的参数是否为空
#         try:
#             if df is None:
#                 raise ValueError("无法正确读取数据，可能是表头行数不正确")
#         except ValueError as e:
#             print(f"错误：{e}")
        
#         if df is not None:
#             #转换为长格式
#             df_melted = pd.melt(df,id_vars=[df.columns[0]],var_name="年份",value_name=indicator_name)
#             # df_melted.rename(columns={df.columns[0]:"地区"},inplace=True) #重命名第一列为地区
#             # print(df_melted) #此处转化没有问题，需要清洗一下最后的注释部分
            
#             #最后的清洗掉注释部分
#             df_melted = df_melted.dropna(subset=["年份"])
#             # print(df_melted) #此处清洗没有问题
            
#             #提取年份数字
#             # df_melted["年份数字"] = df_melted["年份"].astype(str).str.extract(r'(\d{4})')[0] #提取4位数字作为年份，并转换为整数类型
#             # print(f"年份{df_melted['年份数字'].min()}年-{df_melted['年份数字'].max()}年的数据已处理完成")    
#             # df_melted = df_melted.drop(columns=["年份数字"])  
#             all_date.append(df_melted)

#     #先检查有否有成功处理的数据，一共有多少个
#     if all_date:
#         print("===========================================")
#         print(f"成功处理了{len(all_date)}个文件，准备合并")
#     else:
#         print("===========================================")
#         print("没有成功处理任何文件，无法进行合并")
#         return None
    
#     #合并数据
#     print("===========================================")
#     print("开始合并数据")
#     from functools import reduce
    
#     #按照地区和年份进行外连接合并
#     merged =reduce(lambda left,right:pd.merge(left,right,on=["地区","年份"],how="outer"),all_date) 
#     #过滤掉最后的注释行，只保留地区和年份不为空行
#     merged = merged.dropna(subset=["地区","年份"])

#     #保存合并
#     merged.to_csv(output_file,index=False,encoding="utf-8-sig") 
#     print(f"\n所有文件合并完成，共{merged.shape[0]}行 * {merged.shape[1]}列数据")

#     return merged