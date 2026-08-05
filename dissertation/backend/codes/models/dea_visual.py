import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# 导入你的工具库
current_dir = os.path.dirname(os.path.abspath(__file__))
codes_dir = os.path.dirname(current_dir)
sys.path.append(codes_dir)
from utils.common import OUTPUT_PATH, save_figure, plot_style, load_sqldata

class DEAVisualization:
    """DEA 效率分析可视化类"""

    def __init__(self, df_dea):
        """
        :param df_dea: 包含 DEA 结果的 DataFrame (TE, PTE, SE, 冗余等)
        """
        self.df_dea = df_dea
        # 确保年份是字符串方便绘图
        self.df_dea['年份'] = self.df_dea['年份'].astype(str)
        plot_style()

    def plot_efficiency_trends(self):
        """1. 绘制全国平均效率随时间的变化趋势 (TE, PTE, SE)"""
        yearly_avg = self.df_dea.groupby('年份')[['综合效率(TE/CCR)', '纯技术效率(PTE/BCC)', '规模效率(SE)']].mean()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        yearly_avg.plot(kind='line', marker='o', ax=ax, linewidth=2, markersize=8)
        
        ax.set_title('2015-2024年全国医疗配置平均效率演变趋势', fontsize=15, fontweight='bold')
        ax.set_xlabel('年份')
        ax.set_ylabel('效率分值')
        ax.set_ylim(0.7, 1.05) # 效率通常在0.8-1之间波动
        ax.grid(True, alpha=0.3)
        ax.legend(loc='lower right')
        
        save_figure(fig, 'DEA_全国平均效率趋势图.png')
        plt.show()

    def plot_redundancy_ranking(self, year=None):
        """2. 绘制特定年份投入冗余排名（找出资源浪费最严重的地区）"""
        if year is None:
            year = self.df_dea['年份'].max()
        
        year_data = self.df_dea[self.df_dea['年份'] == year].copy()
        # 筛选出非有效且有冗余的地区
        redundant_df = year_data[year_data['有效性'] == '非有效'].sort_values('投入冗余_财政', ascending=False).head(10)
        
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(data=redundant_df, x='投入冗余_财政', y='地区', palette='Reds_r', ax=ax, legend=False)
        
        ax.set_title(f'{year} 财政医疗支出冗余量排名前10地区', fontsize=14)
        ax.set_xlabel('冗余金额 (亿元)')
        ax.set_ylabel('地区')
        
        # 在柱状图上标注具体数值
        for p in ax.patches:
            ax.annotate(f'{p.get_width():.1f}', (p.get_width(), p.get_y() + p.get_height()/2), 
                        ha='left', va='center', xytext=(5, 0), textcoords='offset points')
            
        save_figure(fig, f'DEA_{year}_投入冗余排名图.png')
        plt.show()

    def plot_rts_distribution(self, year=None):
        """3. 规模报酬状态分布情况（饼图）"""
        if year is None:
            year = self.df_dea['年份'].max()
        
        status_counts = self.df_dea[self.df_dea['年份'] == year]['规模报酬类型'].value_counts()
        
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = ['#66b3ff','#99ff99','#ff9999']
        ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', 
               startangle=140, colors=colors, explode=[0.05]*len(status_counts))
        
        ax.set_title(f'{year} 各地区医疗规模报酬状态分布', fontsize=14)
        save_figure(fig, f'DEA_{year}_规模报酬分布饼图.png')
        plt.show()

    def plot_gini_dea_correlation(self, df_gini):
        """
        4. 核心关联性分析：基尼系数 (不公平性) 与 DEA 效率 (产出得分) 的散点相关图
        """
        # 预处理基尼系数数据，取“地方财政医疗卫生支出(亿元)_变异系数”作为公平性代表
        # 注意：这里需要将 DEA 的年份与 Gini 的年份对齐
        # 假设 df_gini 已经包含了变异系数
        
        latest_year = self.df_dea['年份'].max()
        dea_latest = self.df_dea[self.df_dea['年份'] == latest_year]
        
        # 从 Gini 数据中获取对应年份的变异系数 (这里假设你已经从数据库取到了该值)
        # 如果 df_gini 是宽表，需要提取
        cv_val = df_gini.loc[latest_year, '地方财政医疗卫生支出(亿元)_变异系数']
        
        # 关联性逻辑：分析各地区的效率分布
        # 论文论点：资源越集中的地区，其效率表现如何？
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sns.regplot(data=dea_latest, x='纯技术效率(PTE/BCC)', y='规模效率(SE)', 
                    scatter_kws={'s':100, 'alpha':0.5}, line_kws={'color':'red'}, ax=ax)
        
        # 标注部分重点地区
        for i in range(dea_latest.shape[0]):
            if dea_latest.iloc[i]['纯技术效率(PTE/BCC)'] < 0.8 or dea_latest.iloc[i]['规模效率(SE)'] < 0.7:
                ax.text(dea_latest.iloc[i]['纯技术效率(PTE/BCC)'], dea_latest.iloc[i]['规模效率(SE)'], 
                        dea_latest.iloc[i]['地区'], fontsize=9)

        ax.set_title(f'{latest_year} 医疗配置：技术效率与规模效率的相关性分析', fontsize=14)
        ax.set_xlabel('纯技术效率 (管理/技术水平)')
        ax.set_ylabel('规模效率 (资源规模适配度)')
        ax.grid(True, linestyle='--', alpha=0.6)
        
        save_figure(fig, 'DEA_效率关联散点图.png')
        plt.show()

# 集成调用逻辑
if __name__ == "__main__":
    # 1. 加载 DEA 结果
    df_dea_results = load_sqldata("SELECT * FROM dea") # 假设你存入数据库的表名
    
    # 2. 加载 Gini 结果用于关联
    from models.gini import GiniAnalysis
    # 假设 load_gini_data 是你之前代码中定义的加载函数
    # gini_tool = GiniAnalysis(None) 
    # df_gini_wide = gini_tool.load_gini_data(is_db=True, return_long=False)
    
    # 3. 绘图
    visual = DEAVisualization(df_dea_results)
    visual.plot_efficiency_trends()      # 趋势分析
    visual.plot_redundancy_ranking()    # 浪费分析
    visual.plot_rts_distribution()      # 规模状态分析
    # visual.plot_gini_dea_correlation(df_gini_wide) # 关联分析