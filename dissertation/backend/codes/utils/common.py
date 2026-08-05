import os
import sys

#获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
#获取codes目录
codes_dir = os.path.dirname(current_dir)
#获取项目根目录
root = os.path.dirname(codes_dir)
#将项目的根目录添加到sys.path
sys.path.append(root)

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine,text
from codes.config.settings import mysql_config as mc,model_params as mp
import pymysql
import numpy as np

# 定义输出路径（相对于项目根目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = {
    'figures': '论文/output/figures',
    'data': '论文/output/analysis_data',
    'reports': '论文/output/reports'
}
PLOT_FONT_SIZE = 25

def create_output_dir():
    """创建输出文件夹（自动创建，避免报错）"""
    for path in OUTPUT_PATH.values():
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"创建文件夹: {path}")
        else:
            print(f"文件夹已存在: {path}")
    print("输出文件夹检查完成")

#设置绘图样式，统一图表格式
def plot_style():
    plt.rcParams['font.sans-serif'] = ['SimHei'] #中文显示
    plt.rcParams['axes.unicode_minus'] = False #负号显示
    plt.rcParams['figure.figsize'] = (10,6) #默认画布大小
    plt.rcParams['figure.dpi'] = 100 #默认分辨率
    plt.rcParams['axes.grid'] = True #显示网格
    plt.rcParams['grid.alpha'] = 0.3 #网格透明度
    plt.rcParams['figure.autolayout'] = True
    plt.rcParams['font.size'] = PLOT_FONT_SIZE
    plt.rcParams['axes.titlesize'] = PLOT_FONT_SIZE
    plt.rcParams['axes.labelsize'] = PLOT_FONT_SIZE
    plt.rcParams['xtick.labelsize'] = PLOT_FONT_SIZE
    plt.rcParams['ytick.labelsize'] = PLOT_FONT_SIZE
    plt.rcParams['legend.fontsize'] = PLOT_FONT_SIZE
    print("绘图样式设置完成")

#从mysql加载数据
def load_sqldata(words):
    print("正在从数据库加载数据")
    #创建数据库连接
    engine = create_engine(
        f"mysql+pymysql://{mc['user']}:{mc['password']}@{mc['host']}:{mc['port']}/{mc['db']}?charset={mc['charset']}"    
    )

    try:
        #使用with语句创建链接，否则版本问题报错'OptionEngine' object has no attribute 'execute'
        with engine.connect() as conn:
            #加载merged_data表，使用read_sql和read_sql_query都需要text()配合使用
            df = pd.read_sql(text(words),conn)
            print("表加载完成")
            return df

            # df_merged = pd.read_sql(text("SELECT * FROM merged_data"),conn)
            # print("merged_data表加载完成")

            # df_longevity = pd.read_sql_query(text("SELECT * FROM longevity"),conn)
            # print("longevity表加载完成")

            # df_total = pd.read_sql_query(text("SELECT * FROM total_cost"),conn)
            # print("total_cost表加载完成")

            # return df_merged,df_longevity,df_total
    
    except Exception as e:
        print(f"数据加载失败{e}")
        return None,None,None
    
def save_dataframe(df, filename, subdir='data'):
    """保存DataFrame到指定目录"""
    if df is None or df.empty:
        print(f"数据为空，无法保存 {filename}")
        return False
    
    filepath = os.path.join(OUTPUT_PATH[subdir], filename)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"数据已保存：{filepath}")
    return True    

def save_figure(fig, filename, subdir='figures', dpi=300):
    """保存图表到指定目录"""
    if fig is None:
        print(f"图表为空，无法保存 {filename}")
        return False
    
    filepath = os.path.join(OUTPUT_PATH[subdir], filename)
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
    # plt.show()
    plt.close(fig)
    print(f"图表已保存：{filepath}")
    return True

#清洗列明，移除括号和单位，便于后续分析
# def clean_colname(df):
#     if df is None:
#         return None   
#     new_column = {}
#     for col in df.columns:
#         #移除括号单位
#         clean_col = col.split('(')[0].strip()
#         new_column[col] = clean_col
#     return df.rename(columns=new_column)

# def normalize_data(df, columns):
#     """对指定列进行标准化处理（Z-score标准化）"""
#     if df is None or df.empty:
#         return None
    
#     df_norm = df.copy()
#     for col in columns:
#         if col in df.columns:
#             mean = df[col].mean()
#             std = df[col].std()
#             if std > 0:
#                 df_norm[f'{col}_标准化'] = (df[col] - mean) / std
#             else:
#                 df_norm[f'{col}_标准化'] = 0
    
#     return df_norm

def calculate_gini(x):
    """计算基尼系数（通用函数）"""
    x = np.array(x)
    x = x[~np.isnan(x) & (x > 0)]  # 排除NaN和0值
    
    if len(x) == 0:
        return np.nan
    
    x = np.sort(x)
    n = len(x)
    index = np.arange(1, n + 1)
    gini = (np.sum((2 * index - n - 1) * x)) / (n * np.sum(x))
    return gini

def gini_status(gini_value):
    """根据基尼系数判断均衡状态"""
    if pd.isna(gini_value):
        return "数据不足"
    elif gini_value < 0.2:
        return "绝对均衡"
    elif gini_value < 0.3:
        return "较为均衡"
    elif gini_value < 0.4:
        return "相对合理"
    elif gini_value < 0.5:
        return "差距较大"
    else:
        return "差距悬殊"

# def correlation_status(r_value):
#     """根据相关系数判断相关强度"""
#     r_abs = abs(r_value) if not pd.isna(r_value) else 0
    
#     if pd.isna(r_value):
#         return "无法计算"
#     elif r_abs < 0.1:
#         return "无相关"
#     elif r_abs < 0.3:
#         return "弱相关"
#     elif r_abs < 0.5:
#         return "中等相关"
#     elif r_abs < 0.8:
#         return "强相关"
#     else:
#         return "极强相关"
    
# 测试函数
def test_common():
    """测试common.py的基本功能"""
    print("\n========== 测试common.py ==========")
    
    # 测试创建目录
    # create_output_dir()
    
    # 测试绘图样式
    plot_style()
    
    # 测试数据加载
    df_merged, df_longevity, df_total = load_sqldata()
    
    if df_merged is not None:
        print("\nmerged_data前5行预览：")
        print(df_merged.head())
    
    print("\n✅ common.py测试完成")

if __name__ == "__main__":
    test_common()
