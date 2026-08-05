# models/gini.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
codes_dir = os.path.dirname(current_dir)
sys.path.append(codes_dir)
from utils.common import OUTPUT_PATH, calculate_gini, save_dataframe, gini_status, save_figure, plot_style, load_sqldata
from mysql.sql_connect import csv_to_sql

class GiniAnalysis:
    """医疗资源分配基尼系数分析类"""

    def __init__(self, df_merged):
        self.df_merged = df_merged
        # 核心指标定义 (7个指标)
        self.total_resource_cols = [
            '地方财政医疗卫生支出(亿元)', 
            '医疗卫生机构床位数(万张)',
            '医疗卫生机构数(个)'
        ]
        self.per_capita_resource_cols = [
            '人均财政卫生支出(元)', 
            '每万人医疗卫生机构床位数(张)',
            '每万人医疗卫生机构数(个)',
            '每万人拥有卫生技术人员数(人)'
        ]
        self.all_resource_cols = list(dict.fromkeys(self.total_resource_cols + self.per_capita_resource_cols))

        self.resource_names = {
            '地方财政医疗卫生支出(亿元)': '财政卫生支出(总量)',
            '医疗卫生机构床位数(万张)': '床位数(总量)',
            '医疗卫生机构数(个)': '机构数(总量)',

            '人均财政卫生支出(元)': '财政卫生支出(人均)',
            '每万人医疗卫生机构床位数(张)': '床位数(每万人)',
            '每万人医疗卫生机构数(个)': '机构数(每万人)',
            '每万人拥有卫生技术人员数(人)': '技术人员(每万人)',
        }
        self.gini_results = None

    def ensure_per_capita_indicators(self):
        """生成人均/每万人指标"""
        if '年末常住人口(万人)' not in self.df_merged.columns:
            raise KeyError("缺少'年末常住人口(万人)'列")
        
        # 计算人均指标
        if '人均财政卫生支出(元)' not in self.df_merged.columns:
            self.df_merged['人均财政卫生支出(元)'] = (self.df_merged['地方财政医疗卫生支出(亿元)'] * 1e8 / (self.df_merged['年末常住人口(万人)'] * 1e4))
        if '每万人医疗卫生机构床位数(张)' not in self.df_merged.columns:
            self.df_merged['每万人医疗卫生机构床位数(张)'] = (self.df_merged['医疗卫生机构床位数(万张)'] * 1e4 / (self.df_merged['年末常住人口(万人)'] * 10))
        if '每万人医疗卫生机构数(个)' not in self.df_merged.columns:
            self.df_merged['每万人医疗卫生机构数(个)'] = (self.df_merged['医疗卫生机构数(个)'] / (self.df_merged['年末常住人口(万人)'] / 1e4))

    def calculate_yearly_gini(self):
        """
        核心计算逻辑：计算各指标基尼系数，并分别计算年度综合均值、总量均值、人均均值
        """
        print("[基尼分析] 开始执行年度公平性测算...")
        self.ensure_per_capita_indicators()
        years = sorted(self.df_merged['年份'].unique())
        gini_data = []

        for year in years:
            year_data = self.df_merged[self.df_merged['年份'] == year]
            row = {'年份': year}
            
            # 用于存放不同分组的基尼值
            all_vals = []   # 综合（全部7个指标）
            total_vals = [] # 总量指标组
            per_vals = []   # 人均指标组

            for col in self.all_resource_cols:
                values = year_data[col].dropna()
                if len(values) == 0: continue
                
                gini_val = calculate_gini(values)
                row[col] = round(gini_val, 3)
                row[f'{col}_状态'] = gini_status(gini_val)
                
                # 分类收集数据用于计算均值
                all_vals.append(gini_val)
                if col in self.total_resource_cols:
                    total_vals.append(gini_val)
                elif col in self.per_capita_resource_cols:
                    per_vals.append(gini_val)

            # --- 计算该年份三类指标的基尼均值 ---
            # 1. 总量均值 (3 个总量指标)
            row['总量基尼均值'] = round(np.mean(total_vals), 3) if total_vals else 0.0
            # 2. 人均均值 (4 个人均指标)
            row['人均基尼均值'] = round(np.mean(per_vals), 3) if per_vals else 0.0

            gini_data.append(row)

        self.gini_results = pd.DataFrame(gini_data)
        
        # 保存结果到 CSV 和 数据库
        save_dataframe(self.gini_results, '基尼系数.csv')
        try:
            csv_to_sql("论文/output/analysis_data/基尼系数.csv", "gini")
        except Exception as e:
            print(f"[错误] 基尼数据入库失败: {e}")
            
        return self.gini_results


    # ========================== 修改后的可视化部分 ==========================
    def plot_yearly_gini_bar(self, year):
        """
        要求1：每一年的所有指标的基尼系数为一个柱状图 (学术增强版)
        """
        if self.gini_results is None: self.calculate_yearly_gini()
        
        year_data = self.gini_results[self.gini_results['年份'] == year]
        if year_data.empty:
            print(f"警告：未找到 {year} 的基尼数据")
            return

        plot_style()
        fig, ax = plt.subplots(figsize=(13, 8))
        
        # 准备数据
        labels = [self.resource_names.get(col, col) for col in self.all_resource_cols]
        values = [year_data[col].values[0] for col in self.all_resource_cols]
        
        # 设置 Y 轴范围：至少到0.5，覆盖国际标准线
        y_limit = max(max(values) + 0.1, 0.6)

        # --- 核心：图内均衡等级区间划分 (背景色块) ---
        ax.axhspan(0, 0.2, facecolor="#9FD9A3", alpha=0.6, label='绝对均衡区')
        ax.axhspan(0.2, 0.3, facecolor="#A9C984", alpha=0.7, label='较为均衡区')
        ax.axhspan(0.3, 0.4, facecolor="#E4CEAA", alpha=0.8, label='相对合理区')
        ax.axhspan(0.4, 0.5, facecolor="#F8C0C8", alpha=0.6, label='差距较大区')
        ax.axhspan(0.5, y_limit, facecolor="#D26CBA", alpha=0.6, label='差距悬殊区')
        

        # 绘制分界参考线
        for line_val, color in zip([0.2, 0.3, 0.4, 0.5], ["#6BD76F", "#729747", "#E77169", "#D26CBA"]):
            ax.axhline(line_val, color=color, linestyle='--', linewidth=1, alpha=0.5)

        # 绘制柱状图
        # 根据值所属区间分配颜色
        bar_colors = ["#315233" if v <= 0.2 else "#66B52E" if v <= 0.3 else "#F18731" if v <= 0.4 else '#C62828' for v in values]
        bars = ax.bar(labels, values, color=bar_colors, edgecolor='white', linewidth=1.5, zorder=3, width=0.6)
        
        # 标注数值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.005, f'{height:.4f}', 
                    ha='center', va='bottom', fontweight='bold', fontsize=10, color='#333333', zorder=4)

        # 图表装饰
        # ax.set_title(f'{year} 医疗资源配置公平性对比分析 (Gini)', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('基尼系数 (Gini Coefficient)', fontsize=30, labelpad=10)
        ax.set_ylim(0, y_limit)
        
        # 优化坐标轴显示
        plt.xticks(rotation=25, ha='right', fontsize=30)
        ax.grid(axis='y', linestyle=':', alpha=0.3, zorder=0)
        
        # 图内解释说明（Legend 放置在图内）
        ax.legend(loc='upper right', frameon=True, shadow=True, title="公平性等级说明", fontsize=30, title_fontsize=10)

        plt.tight_layout()
        save_figure(fig, f'Gini对比图_{year}.png')
        plt.show()

    def plot_indicator_trend_line(self, indicator_col):
        """
        要求2：每个指标十年的基尼系数变化的折线图 (学术增强版)
        """
        if self.gini_results is None: self.calculate_yearly_gini()
        
        if indicator_col not in self.gini_results.columns:
            return

        plot_style()
        fig, ax = plt.subplots(figsize=(12, 7))
        
        years = self.gini_results['年份']
        values = self.gini_results[indicator_col]
        friendly_name = self.resource_names.get(indicator_col, indicator_col)
        
        y_limit = max(values.max() + 0.1, 0.6)

        # --- 核心：图内均衡等级区间划分 (背景填充) ---
        ax.axhspan(0, 0.2, facecolor="#A9DCAD", alpha=0.6)
        ax.axhspan(0.2, 0.3, facecolor="#99B57A", alpha=0.7)
        ax.axhspan(0.3, 0.4, facecolor="#E9D1AB", alpha=0.8)
        ax.axhspan(0.4, 0.5, facecolor="#F1B7C2", alpha=0.6)
        ax.axhspan(0.5, y_limit, facecolor="#D26CBA", alpha=0.6)

        # 在图内右侧直接标注等级文字（代替部分图例，更直观）
        text_style = dict(fontsize=20, fontweight='bold', alpha=0.6, verticalalignment='center')
        ax.text(years.iloc[-1], 0.1, "绝对均衡", color="#094A0C", **text_style)
        ax.text(years.iloc[-1], 0.25, "较为均衡", color="#4E7D2C", **text_style)
        ax.text(years.iloc[-1], 0.35, "相对合理", color="#696910", **text_style)
        ax.text(years.iloc[-1], 0.45, "差距较大", color="#8A3838", **text_style)
        ax.text(years.iloc[-1], 0.55, "差距悬殊", color="#A36A9A", **text_style)

        # 绘制参考线
        for line_val, color in zip([0.2, 0.3, 0.4, 0.5], ["#2DA131", "#D2C72C", '#F44336', '#D26CBA']):
            ax.axhline(line_val, color=color, linestyle='--', linewidth=1.2, alpha=0.4, zorder=1)

        # 绘制主趋势折线
        # 使用深蓝色代表核心轨迹
        ax.plot(years, values, marker='D', markersize=9, markerfacecolor='white', markeredgewidth=2,
                color='#1A237E', linewidth=3, label='基尼系数演变轨迹', zorder=5)
        
        # 标注数值
        for x, y in zip(years, values):
            ax.text(x, y + 0.015, f'{y:.4f}', ha='center', va='bottom', 
                    fontsize=18, fontweight='bold', color="#1D1D25", zorder=6)

        # 图表装饰
        # ax.set_title(f'2015-2024 {friendly_name} 配置公平性演变趋势', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('年份 (Year)', fontsize=25)
        ax.set_ylabel('基尼系数 (Gini Coefficient)', fontsize=25)
        plt.xticks(rotation=45, ha='right', fontsize=18)

        ax.set_ylim(0, y_limit)
        ax.grid(True, linestyle=':', alpha=0.3, zorder=0)
        
        # 图内图例
        ax.legend(loc='upper left', frameon=True, shadow=True, fontsize=20)

        plt.tight_layout()
        save_figure(fig, f'Gini趋势分析_{friendly_name}.png')
        plt.show()

if __name__ == "__main__":
    # 模拟运行
    df_test = load_sqldata("SELECT * FROM merged_data")
    if df_test is not None:
        analysis = GiniAnalysis(df_test)
        analysis.calculate_yearly_gini()
        year_list = ["2024年", "2023年", "2022年", "2021年", "2020年", "2019年", "2018年", "2017年", "2016年", "2015年"]
        # for year in year_list:
            # analysis.plot_yearly_gini_bar(year)
        for indicator in analysis.all_resource_cols:
            analysis.plot_indicator_trend_line(indicator)