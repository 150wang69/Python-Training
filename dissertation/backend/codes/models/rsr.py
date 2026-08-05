import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
codes_dir = os.path.dirname(current_dir)
sys.path.append(codes_dir)
from utils.common import load_sqldata, save_dataframe, save_figure, plot_style, create_output_dir
from mysql.sql_connect import csv_to_sql

class DEAValidationRSR:
    """基于 RSR (秩和比法) 的 DEA 结果验证模块"""
    
    def __init__(self, df_merged, df_dea, input_cols, output_cols):
        self.df_merged = df_merged.copy()
        self.df_dea = df_dea.copy()
        self.input_cols = input_cols
        self.output_cols = output_cols

    def run_rsr_analysis(self, year):
        """
        方案：秩和比法 (RSR) 综合评价
        逻辑：将“表现越好”的指标赋予“越高”的秩次
        """
        print(f"\n[验证] 正在执行 {year} 秩和比法 (RSR) 综合评价...")
        data = self.df_merged[self.df_merged['年份'] == year].copy()
        if data.empty:
            return pd.DataFrame()
        
        regions = data['地区'].values
        rank_df = pd.DataFrame({'地区': regions})
        
        # 1. 投入指标 (越小越好)
        # 使用 ascending=False 意味着：数值越小，秩次(排名)越大
        for col in self.input_cols:
            rank_df[f'R_{col}'] = data[col].rank(ascending=False).values
            
        # 2. 产出指标 (越大越好)
        # 使用 ascending=True 意味着：数值越大，秩次(排名)越大
        for col in self.output_cols:
            rank_df[f'R_{col}'] = data[col].rank(ascending=True).values
            
        # 3. 计算 RSR 值
        rank_cols = [col for col in rank_df.columns if col.startswith('R_')]
        rank_df['Rank_Sum'] = rank_df[rank_cols].sum(axis=1)
        
        n = len(regions)
        m = len(self.input_cols) + len(self.output_cols)
        
        # 计算最终 RSR 得分：得分越高，代表综合表现越好
        rank_df['RSR得分'] = (rank_df['Rank_Sum'] / (n * m)).round(3)
        
        # print(f"RSR:{rank_df}")
        
        return rank_df

    def verify_consistency(self, year):

        """
        跨方法一致性检验：DEA 效率 vs RSR 综合评价
        """
        print(f"[验证] 正在计算 DEA 与 RSR 的相关性系数...")
        
        # 1. 提取 DEA 效率数据
        dea_yr = self.df_dea[self.df_dea['年份'] == year][['地区', '综合效率(TE)']]
        print(f'提取{year}的数据成功')
        
        # 2. 计算 RSR 综合得分
        rsr_yr = self.run_rsr_analysis(year)
        # print(f"{year}的rsr是{rsr_yr}")
        
        if rsr_yr.empty:
            print(f"错误：未找到 {year} 的数据，无法验证")
            return None

        # 3. 合并数据表进行比对
        compare_df = pd.merge(dea_yr, rsr_yr, on='地区')
        
        # 4. 计算 Spearman 相关系数
        corr, p_value = spearmanr(compare_df['综合效率(TE)'], compare_df['RSR得分'])
        
        # compare_df['年份'] = year
        compare_df.insert(0, '年份', year)
        compare_df['Spearman相关系数'] = round(corr,3)
        compare_df['P值'] = p_value

        print("\n" + "="*50)
        print(f"验证年份: {year}")
        print(f"Spearman 秩相关系数: {corr:.3f}")
        print(f"P 值 (显著性级别): {p_value}")
        print("="*50)
        
        # 5. 结论判定
        if p_value < 0.05:
            if corr >= 0.5:
                print("【验证通过】两组评价结果呈显著强正相关，DEA 模型计算准确可信。")
                compare_df['相关性'] = "强正相关"
            elif corr > 0:
                print("【验证基本通过】呈正相关关系，模型具有一定的一致性。")
                compare_df['相关性'] = "正相关"
            else:
                print("【异常】呈负相关，请检查原始数据编秩方向或效率计算逻辑。")
                compare_df['相关性'] = "负相关"
        else:
            print("【结论】未通过显著性检验。相关性不明显，可能是由于样本量较小或两种方法测算侧重点差异较大。")
            compare_df['相关性'] = "不显著"

        print(f"合并后的数据{compare_df.shape[0]}条")    
        return compare_df
    
    def plot_validation_scatter(self,compare_df,year):
        # plt.switch_backend('Agg')  # 使用非交互式后端，适合服务器环境
        fig = plt.figure(figsize=(10, 7))
        sns.regplot(data=compare_df, x='RSR得分', y='综合效率(TE)', 
                    scatter_kws={'s':100, 'color':'#1E88E5'}, 
                    line_kws={'color':'red', 'linestyle':'--'})
        
        # 标注部分省份名称
        for i, row in compare_df.iterrows():
            if row['综合效率(TE)'] > 0.9 or row['RSR得分'] > 0.7: # 只标注表现优秀的
                plt.text(row['RSR得分'], row['综合效率(TE)'], row['地区'], fontsize=9)
                
        plt.title(f"DEA 效率值与 RSR 综合得分相关性验证{year}", fontsize=14, fontweight='bold')
        plt.xlabel("RSR 综合评价得分", fontsize=12)
        plt.ylabel("DEA 综合效率 (TE)", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        # plt.show()
        save_figure(fig, f"DEA_RSR_相关性_{year}.png")

    def save_rsr_data(self, start_year=2015, end_year=2024):
        all_data = []  # 用来装每一年的 compare_df
        
        for year in range(start_year, end_year + 1):
            year_name = f"{year}年"
            print(f"\n====== 正在处理：{year_name} ======")
            
            # 执行验证，拿到当年的表
            df_year = self.verify_consistency(year_name)
            
            # 如果有数据，就加进去
            if df_year is not None and not df_year.empty:
                all_data.append(df_year)

        # 合并所有年份
        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            
            # 保存为 CSV
            # final_df.to_csv("DEA_RSR_相关性.csv", index=False, encoding="utf-8-sig")
            save_dataframe(final_df, "DEA_RSR_相关性.csv")
            print(f"\n✅ 全部完成！已合并保存：DEA_RSR_相关性.csv")
            csv_to_sql("论文/output/analysis_data/DEA_RSR_相关性.csv", "rsr")
            return final_df
        else:
            print("❌ 没有数据可保存")
            return None