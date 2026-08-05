import numpy as np
import pandas as pd
from scipy.stats import spearmanr

class RobustnessAndComparison:
    """数据验证与横向对比模块"""
    
    def __init__(self, df_merged, df_dea, input_cols, output_cols):
        self.df_merged = df_merged.copy()
        self.df_dea = df_dea.copy()
        self.all_cols = input_cols + output_cols

    def run_entropy_topsis(self, year="2024年"):
        """
        方案：熵权 TOPSIS 综合评价 (横向对比方法)
        支撑文献：Hwang & Yoon (1981)
        """
        print(f"\n[验证] 执行 {year} 熵权 TOPSIS 综合评价分析...")
        data = self.df_merged[self.df_merged['年份'] == year].copy()
        regions = data['地区'].values
        X = data[self.all_cols].values
        
        # 1. 归一化 (标准化)
        X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-9)
        
        # 2. 熵权法计算权重
        P = X_norm / (X_norm.sum(axis=0) + 1e-9)
        e = -1 / np.log(len(X)) * (P * np.log(P + 1e-9)).sum(axis=0)
        d = 1 - e
        weights = d / d.sum()
        
        # 3. 计算 TOPSIS 综合得分
        Z = X_norm * weights
        ideal_best = Z.max(axis=0)
        ideal_worst = Z.min(axis=0)
        
        d_best = np.sqrt(((Z - ideal_best)**2).sum(axis=1))
        d_worst = np.sqrt(((Z - ideal_worst)**2).sum(axis=1))
        
        scores = d_worst / (d_best + d_worst)
        
        res_topsis = pd.DataFrame({'地区': regions, 'TOPSIS综合得分': scores})
        return res_topsis

    def verify_consistency(self, year="2024年"):
        """
        方案：一致性检验 (Spearman 秩相关分析)
        用于验证 DEA 效率与 TOPSIS 综合评价的一致性
        """
        print(f"[验证] 正在执行 DEA 与 TOPSIS 的横向一致性验证...")
        
        # 获取该年的 DEA 数据
        dea_yr = self.df_dea[self.df_dea['年份'] == year][['地区', '综合效率(TE)']]
        # 获取该年的 TOPSIS 数据
        topsis_yr = self.run_entropy_topsis(year)
        
        # 合并
        compare_df = pd.merge(dea_yr, topsis_yr, on='地区')
        
        # 计算 Spearman 相关系数 (秩相关)
        corr, p_value = spearmanr(compare_df['综合效率(TE)'], compare_df['TOPSIS综合得分'])
        
        print(f"--- 验证结果 ---")
        print(f"Spearman 相关系数: {corr:.4f}")
        print(f"P 值: {p_value:.4e}")
        
        if corr > 0.6 and p_value < 0.05:
            print("结论：两种计算方法在显著性水平下高度正相关，数据具有极强的一致性和可信度。")
        else:
            print("结论：两种方法侧重点不同，DEA 侧重转化，TOPSIS 侧重规模，建议在论文中进行分类讨论。")
            
        return compare_df

    def plot_quadrant_analysis(compare_df):
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 8))
        
        # 计算均值作为象限分割线
        mean_dea = compare_df['综合效率(TE)'].mean()
        mean_topsis = compare_df['TOPSIS综合得分'].mean()
        
        plt.axhline(mean_dea, color='gray', linestyle='--', alpha=0.5)
        plt.axvline(mean_topsis, color='gray', linestyle='--', alpha=0.5)
        
        # 绘点
        plt.scatter(compare_df['TOPSIS综合得分'], compare_df['综合效率(TE)'], s=100, color='skyblue')
        
        # 标注地区
        for i, row in compare_df.iterrows():
            plt.text(row['TOPSIS综合得分'], row['综合效率(TE)'], row['地区'], fontsize=9)
            
        plt.xlabel('TOPSIS 综合评价得分 (资源充裕度)')
        plt.ylabel('DEA 综合效率 (配置有效性)')
        plt.title('各地区医疗资源“规模-效率”四象限联动分析')
        
        # 添加象限标签
        plt.text(compare_df['TOPSIS综合得分'].max()*0.8, compare_df['综合效率(TE)'].max()*0.9, "I: 协同标杆区", color='red')
        plt.text(compare_df['TOPSIS综合得分'].min(), compare_df['综合效率(TE)'].max()*0.9, "II: 效率领先型", color='blue')
        plt.text(compare_df['TOPSIS综合得分'].max()*0.8, compare_df['综合效率(TE)'].min(), "IV: 资源冗余型", color='orange')
        
        plt.show()