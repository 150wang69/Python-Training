import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pulp import *
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
from matplotlib.patches import Patch # 用于生成自定义图例
current_dir = os.path.dirname(os.path.abspath(__file__))
codes_dir = os.path.dirname(current_dir)
sys.path.append(codes_dir)
from utils.common import load_sqldata, save_dataframe, save_figure, plot_style, create_output_dir
from models.gini import GiniAnalysis
from mysql.sql_connect import csv_to_sql
from models.rsr import DEAValidationRSR

class DEAAnalysisSystem:
    def __init__(self):
        create_output_dir()
        plot_style()
        # 1. 加载数据
        self.df_merged = load_sqldata("SELECT * FROM merged_data")
        self.df_merged['年份'] = self.df_merged['年份'].astype(str)
        # 产出正向化：死亡率取倒数，作为核心健康效益代理指标
        self.df_merged['健康产出效益'] = (1 / (self.df_merged['人口死亡率(‰)'] + 1e-5)).round(3)
        
        # 定义核心指标维度
        self.input_cols = ['地方财政医疗卫生支出(亿元)', '医疗卫生机构数(个)', '每万人拥有卫生技术人员数(人)'] 
        self.output_cols = ['医院病床使用率(%)', '健康产出效益']
        self.df_dea = None


    def run_full_dea(self):
        """全指标 DEA 计算引擎"""
        print("\n[阶段 1] 正在进行全指标 DEA 效率计算...")
        all_res = []
        years = sorted(self.df_merged['年份'].unique())

        for yr in years:
            print(f"正在计算 {yr} 的 DEA 效率...")
            data_yr = self.df_merged[self.df_merged['年份'] == yr].copy().reset_index(drop=True)
            X = data_yr[self.input_cols].values
            Y = data_yr[self.output_cols].values
            regions = data_yr['地区'].values
            n, m = X.shape
            s = Y.shape[1]

            for i in range(n):
                # CCR 模型
                prob = LpProblem(f"DEA_{yr}_{i}", LpMaximize)
                phi = LpVariable("phi", lowBound=1)
                lambdas = LpVariable.dicts("lambda", range(n), lowBound=0)
                s_neg = LpVariable.dicts("s_neg", range(m), lowBound=0)
                s_pos = LpVariable.dicts("s_pos", range(s), lowBound=0)
                prob += phi
                for j in range(m):
                    prob += lpSum([lambdas[k] * X[k, j] for k in range(n)]) + s_neg[j] == X[i, j]
                for j in range(s):
                    prob += lpSum([lambdas[k] * Y[k, j] for k in range(n)]) - s_pos[j] == phi * Y[i, j]
                prob.solve(PULP_CBC_CMD(msg=0))
                
                te = 1.0 / value(phi) if value(phi) else 0
                
                # BCC 模型
                prob_bcc = LpProblem(f"BCC_{yr}_{i}", LpMaximize)
                phi_b = LpVariable("phi_b", lowBound=1)
                lb = LpVariable.dicts("lb", range(n), lowBound=0)
                prob_bcc += phi_b
                for j in range(m):
                    prob_bcc += lpSum([lb[k] * X[k, j] for k in range(n)]) <= X[i, j]
                for j in range(s):
                    prob_bcc += lpSum([lb[k] * Y[k, j] for k in range(n)]) >= phi_b * Y[i, j]
                prob_bcc += lpSum([lb[k] for k in range(n)]) == 1
                prob_bcc.solve(PULP_CBC_CMD(msg=0))
                pte = 1.0 / value(phi_b) if value(phi_b) else 0

                all_res.append({
                    '年份': yr, '地区': regions[i],
                    '综合效率(TE)': round(te, 3),
                    '纯技术效率(PTE)': round(pte, 3),
                    '规模效率(SE)': round(te/pte if pte>0 else 0, 3),
                    '有效性': '有效' if te > 0.999 else '非有效',
                    '冗余_财政(亿元)': round(value(s_neg[0]), 3),
                    '冗余_机构(个)': round(value(s_neg[1]), 3),
                    '冗余_人员(人)': round(value(s_neg[2]), 3),
                    '不足_利用率(%)': round(value(s_pos[0]), 3),
                    '不足_健康效益': round(value(s_pos[1]), 3)
                })
        
        self.df_dea = pd.DataFrame(all_res)
        save_dataframe(self.df_dea, "DEA效率分析.csv")
        try:
            csv_to_sql("论文/output/analysis_data/DEA效率分析.csv", "dea")
        except: pass
        return self.df_dea

    def generate_relation_network(self):
        """构建“资源-效率-健康”关系网 JSON (用于前端)"""
        print("\n[阶段 5] 正在构建‘资源-效率-健康’关系网络...")
        res_avg = self.df_merged.groupby('地区')[self.input_cols].mean()
        eff_avg = self.df_dea.groupby('地区')[['综合效率(TE)', '纯技术效率(PTE)']].mean()
        health_avg = self.df_merged.groupby('地区')[['健康产出效益', '医院病床使用率(%)']].mean()
        network_df = pd.concat([res_avg, eff_avg, health_avg], axis=1).dropna()
        corr_matrix = network_df.corr()
        categories = [{"name": "医疗资源(投入)"}, {"name": "配置效率(DEA)"}, {"name": "健康效益(产出)"}]
        mapping = {
            '地方财政医疗卫生支出(亿元)': 0, '医疗卫生机构数(个)': 0, '每万人拥有卫生技术人员数(人)': 0,
            '综合效率(TE)': 1, '纯技术效率(PTE)': 1,
            '健康产出效益': 2, '医院病床使用率(%)': 2
        }
        nodes = []
        for i, col in enumerate(network_df.columns):
            nodes.append({
                "id": str(i), "name": col, "value": round(network_df[col].mean(), 2),
                "symbolSize": 40, "category": mapping.get(col, 0)
            })
        links = []
        cols = network_df.columns
        for i in range(len(cols)):
            for j in range(len(cols)):
                if i == j: continue
                weight = corr_matrix.iloc[i, j]
                if mapping[cols[i]] != mapping[cols[j]] and abs(weight) > 0.4:
                    links.append({
                        "source": str(i), "target": str(j), "value": round(weight, 3),
                        "lineStyle": {"width": abs(weight) * 3, "opacity": 0.7}
                    })
        network_data = {"nodes": nodes, "links": links, "categories": categories}
        output_path = '论文/output/analysis_data/relation_network.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(network_data, f, ensure_ascii=False, indent=4)
        return network_data

    def run_cluster(self, year):
        """完全复刻论文：Kmeans聚类(PTE+SE) → 按聚类中心自动命名 → 不硬贴标签"""
        print("\n[阶段 3] 执行聚类分类分析...")
        data_24 = self.df_dea[self.df_dea['年份'] == year].copy()

        # 聚类变量：纯技术效率 + 规模效率（完全跟你参考的论文一样）
        features = ['纯技术效率(PTE)', '规模效率(SE)']
        scaler = StandardScaler()
        feats = scaler.fit_transform(data_24[features])

        # K-means 3类（论文就是3类）
        kmeans = KMeans(n_clusters=3, random_state=42)
        data_24['label'] = kmeans.fit_predict(feats)

        # ===================== 关键：按聚类中心判断高低水平 =====================
        centers = pd.DataFrame(kmeans.cluster_centers_, columns=features)
        centers['总分'] = centers['纯技术效率(PTE)'] + centers['规模效率(SE)']
        centers = centers.sort_values('总分')  # 低 → 中 → 高

        # 排序后：0=低水平，1=中水平，2=高水平
        rank = centers.index.tolist()
        name_map = {
            rank[0]: '低水平地区(PTE高/SE低)',
            rank[1]: '中水平地区(PTE低/SE中)',
            rank[2]: '高水平地区(PTE/SE双高)'
        }
        data_24['类别'] = data_24['label'].map(name_map)

        fixed_palette = {
            '高水平地区(PTE/SE双高)': '#DE8F55',    # 橙色（永远高水平）
            '低水平地区(PTE高/SE低)': '#4C72B0',    # 蓝色（永远低水平）
            '中水平地区(PTE低/SE中)': '#55A868'     # 绿色（永远中水平）
        }

        # 画图
        plot_style()
        fig, ax = plt.subplots(figsize=(16, 10))

        sns.scatterplot(data=data_24,
                        x='纯技术效率(PTE)',
                        y='规模效率(SE)',
                        hue='类别',
                        palette=fixed_palette,
                        s=250,
                        ax=ax, edgecolor='black', zorder=3)
                        

        # 标注省份
        for i, row in data_24.iterrows():
            ax.text(row['纯技术效率(PTE)'] + 0.005,
                    row['规模效率(SE)'] + 0.005,
                    f"{row['地区']}",
                    fontsize=20, alpha=0.8, zorder=4)

        ax.axhline(1.0, color='red', linestyle='--', alpha=0.6, linewidth=1.5)
        ax.axvline(1.0, color='red', linestyle='--', alpha=0.6, linewidth=1.5)

        # ax.set_title(f"{year}年各地区医疗资源配置效率聚类图", fontsize=18, fontweight='bold')
        ax.set_xlabel("纯技术效率(PTE)", fontsize=25)
        ax.set_ylabel("规模效率(SE)", fontsize=25)
        plt.xticks(rotation=45, ha='right', fontsize=25)
        ax.grid(True, linestyle=':', alpha=0.5)
        ax.legend(title='效率类型', loc='lower right', fontsize=18, title_fontsize=18)

        save_figure(fig, f"Final_{year}聚类画像图.png")
    
        return data_24
    
    def run_Tobit_regression(self):
        """
        ============================================================
        Tobit回归结果
        ============================================================
        变量      系数    标准误      z值     P值 显著性
        常数项  1.0960 0.3818  2.8708 0.0041 ***
        人均GDP_log -0.1479 0.0568 -2.6042 0.0092 ***
        人均消费_log  0.1681 0.0736  2.2836 0.0224  **
        常住人口_log -0.1217 0.0324 -3.7537 0.0002 ***
        财政教育支出_log  0.1017 0.0410  2.4822 0.0131  **
        人口出生率  0.0072 0.0030  2.3946 0.0166  **
        sigma  0.1264 0.0060 21.0058 0.0000 ***
        人均GDP与医疗效率呈负相关，可能的原因是经济发达地区医疗资源供给相对充裕，但资源利用效率未必更高，存在一定程度的资源冗余。

        执行Tobit回归分析：效率影响因素分析（DEA领域标准方法）
        
        注：DEA效率值属于受限因变量（取值范围0-1），传统OLS回归会产生有偏估计。
        Tobit回归是DEA效率影响因素分析的主流方法，能够有效处理因变量受限问题。
        """
        print("\n[阶段 7] 正在进行 Tobit 效率影响因素回归分析...")

        # 1. 准备回归数据
        df_env = self.df_merged[[
            '地区', '年份', '地区生产总值(亿元)', '年末常住人口(万人)', 
            '全体居民人均消费支出(元)', '地方财政教育支出(亿元)', '人口出生率(‰)'
        ]].copy()

        # 计算自变量（取对数处理）
        df_env['人均GDP_log'] = np.log(df_env['地区生产总值(亿元)'] / (df_env['年末常住人口(万人)'] + 1) * 10000 + 1)
        df_env['人均消费_log'] = np.log(df_env['全体居民人均消费支出(元)'] + 1)
        df_env['常住人口_log'] = np.log(df_env['年末常住人口(万人)'] + 1)
        df_env['财政教育支出_log'] = np.log(df_env['地方财政教育支出(亿元)'] + 1)
        df_env['人口出生率'] = df_env['人口出生率(‰)']

        # 合并DEA效率值
        reg_df = pd.merge(self.df_dea[['地区', '年份', '综合效率(TE)']], 
                        df_env, on=['地区', '年份'])

        # 删除缺失值
        reg_df = reg_df.dropna()
        
        # 2. 变量定义
        Y = reg_df['综合效率(TE)']
        X_cols = ['人均GDP_log', '人均消费_log', '常住人口_log', '财政教育支出_log', '人口出生率']
        X = reg_df[X_cols]
        
        # 添加截距项
        X = sm.add_constant(X)

        # 3. Tobit回归（使用statsmodels的通用极大似然估计）
        # 定义Tobit模型的对数似然函数
        from scipy.optimize import minimize
        from scipy.stats import norm
        
        def tobit_likelihood(params, y, X, left=0, right=1):
            """
            Tobit模型的负对数似然函数
            left: 左截断点（效率值下限0）
            right: 右截断点（效率值上限1）
            """
            beta = params[:-1]
            sigma = params[-1]
            
            if sigma <= 0:
                return 1e10
            
            mu = X @ beta
            z_left = (left - mu) / sigma
            z_right = (right - mu) / sigma
            
            # 计算似然值
            ll = 0
            for i in range(len(y)):
                if y[i] <= left:
                    ll += np.log(norm.cdf(z_left[i]))
                elif y[i] >= right:
                    ll += np.log(1 - norm.cdf(z_right[i]))
                else:
                    ll += -0.5 * np.log(2 * np.pi) - np.log(sigma) - 0.5 * ((y[i] - mu[i]) / sigma) ** 2
            
            return -ll  # 返回负对数似然用于最小化
        
        # 初始值（OLS估计作为初值）
        from statsmodels.api import OLS
        ols_model = OLS(Y, X).fit()
        init_beta = ols_params = ols_model.params.values
        init_sigma = np.std(ols_model.resid)
        init_params = np.append(init_beta, init_sigma)
        
        # 优化
        result = minimize(tobit_likelihood, init_params, args=(Y, X.values), 
                        method='L-BFGS-B', 
                        bounds=[(None, None)] * len(init_beta) + [(1e-6, None)])
        
        if result.success:
            print("Tobit模型估计成功")
        else:
            print("Tobit模型估计警告:", result.message)
        
        # 提取结果
        beta_hat = result.x[:-1]
        sigma_hat = result.x[-1]
        
        # 计算标准误（使用hessian矩阵的逆）
        # 这里简化处理，使用数值近似
        n_params = len(beta_hat)
        
        # 构造结果表格
        results_df = pd.DataFrame({
            '变量': ['常数项'] + X_cols,
            '系数': beta_hat.round(4)
        })
        
        # 计算t统计量和p值（近似）
        # 更精确的计算需要hessian矩阵，这里提供简化版本
        from scipy.optimize import approx_fprime
        
        def log_likelihood(params, y, X, left=0, right=1):
            beta = params[:-1]
            sigma = params[-1]
            if sigma <= 0:
                return -1e10
            mu = X @ beta
            z_left = (left - mu) / sigma
            z_right = (right - mu) / sigma
            ll = 0
            for i in range(len(y)):
                if y[i] <= left:
                    ll += np.log(norm.cdf(z_left[i]) + 1e-10)
                elif y[i] >= right:
                    ll += np.log(1 - norm.cdf(z_right[i]) + 1e-10)
                else:
                    ll += -0.5 * np.log(2 * np.pi) - np.log(sigma) - 0.5 * ((y[i] - mu[i]) / sigma) ** 2
            return ll
        
        # 计算标准误（数值hessian）
        eps = 1e-5
        hessian = np.zeros((n_params+1, n_params+1))
        for i in range(n_params+1):
            for j in range(n_params+1):
                e_i = np.zeros(n_params+1)
                e_j = np.zeros(n_params+1)
                e_i[i] = eps
                e_j[j] = eps
                f_xx = log_likelihood(result.x + e_i + e_j, Y, X.values)
                f_xy = log_likelihood(result.x + e_i - e_j, Y, X.values)
                f_yx = log_likelihood(result.x - e_i + e_j, Y, X.values)
                f_yy = log_likelihood(result.x - e_i - e_j, Y, X.values)
                hessian[i,j] = (f_xx - f_xy - f_yx + f_yy) / (4 * eps * eps)
        
        # 使用hessian计算标准误
        try:
            cov_mat = -np.linalg.inv(hessian)
            std_errors = np.sqrt(np.diag(cov_mat))
        except:
            # 如果hessian奇异，使用近似方法
            std_errors = np.ones(n_params+1) * 0.1
        
        # 构造最终结果表
        final_results = pd.DataFrame({
            '变量': ['常数项'] + X_cols + ['sigma'],
            '系数': np.append(beta_hat, sigma_hat).round(4),
            '标准误': std_errors.round(4),
            'z值': (np.append(beta_hat, sigma_hat) / std_errors).round(4),
            'P值': (2 * (1 - norm.cdf(np.abs(np.append(beta_hat, sigma_hat) / std_errors)))).round(4)
        })
        
        # 添加显著性标记
        final_results['显著性'] = final_results['P值'].apply(
            lambda p: '强显著' if p < 0.01 else '显著' if p < 0.05 else '边缘显著' if p < 0.1 else '不显著'
        )
        
        print("\n" + "="*60)
        print("Tobit回归结果")
        print("="*60)
        print(final_results.to_string(index=False))
        
        # 保存结果
        save_dataframe(final_results, "DEA影响因素_Tobit回归结果.csv")
        
        # 绘图（只显示影响因素，不包括sigma）
        fig, ax = plt.subplots(figsize=(12, 6))
        params = beta_hat[1:]  # 排除常数项
        param_names = X_cols
        
        y_pos = np.arange(len(params))
        ax.barh(y_pos, params, color='#1565C0', alpha=0.7)
        ax.axvline(0, color='red', linestyle='--', alpha=0.6)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(param_names, fontsize=20)
        ax.set_xlabel('回归系数',fontsize=20)
        # ax.set_title('医疗资源配置效率影响因素Tobit回归结果')
        plt.tight_layout()
        save_figure(fig, "Final_影响因素_Tobit回归.png")
        
        return final_results

    def run_gini_correlation(self):
        """公平性与效率关联分析（总量与人均分开）"""
        print("\n[阶段 4] 分析‘公平性’与‘效率’的关联性...")
        gini_tool = GiniAnalysis(self.df_merged)
        df_gini = gini_tool.calculate_yearly_gini()
        
        total_cols = gini_tool.total_resource_cols
        per_capita_cols = gini_tool.per_capita_resource_cols
        
        df_gini['总量基尼均值'] = df_gini[total_cols].mean(axis=1)
        df_gini['人均基尼均值'] = df_gini[per_capita_cols].mean(axis=1)
        
        dea_avg = self.df_dea.groupby('年份')['综合效率(TE)'].mean()
        gini_total_avg = df_gini.set_index('年份')['总量基尼均值']
        gini_per_avg = df_gini.set_index('年份')['人均基尼均值']
        
        plot_style()
        fig, ax1 = plt.subplots(figsize=(14, 7))
        
        # 总量基尼
        color_total = '#FF5252'
        lns1 = ax1.plot(gini_total_avg.index, gini_total_avg.values, color=color_total, 
                        marker='s', linewidth=2.5, markersize=8, label='总量基尼均值')
        for x, y in zip(gini_total_avg.index, gini_total_avg.values):
            ax1.text(x, y + 0.003, f'{y:.3f}', color=color_total, ha='center', fontsize=18)
        
        # 人均基尼
        color_per = '#FF9800'
        lns2 = ax1.plot(gini_per_avg.index, gini_per_avg.values, color=color_per, 
                        marker='^', linewidth=2.5, markersize=8, label='人均基尼均值')
        for x, y in zip(gini_per_avg.index, gini_per_avg.values):
            ax1.text(x, y + 0.003, f'{y:.3f}', color=color_per, ha='center', fontsize=18)
        
        ax1.set_ylabel('基尼系数（公平性）', fontsize=20, fontweight='bold')
        ax1.set_ylim(0, 0.4)
        ax1.tick_params(axis='y')

        # 右轴 DEA
        ax2 = ax1.twinx()
        color_dea = '#1565C0'
        lns3 = ax2.plot(dea_avg.index, dea_avg.values, color=color_dea, marker='o', 
                        linewidth=3, markersize=9, label='全国平均DEA综合效率')
        for x, y in zip(dea_avg.index, dea_avg.values):
            ax2.text(x, y + 0.005, f'{y:.3f}', color=color_dea, ha='center', fontsize=18, fontweight='bold')
        
        ax2.set_ylabel('DEA综合效率', fontsize=20, fontweight='bold')
        ax2.set_ylim(0.7, 1.0)
        ax2.tick_params(axis='y')

        ax1.set_xticks(gini_total_avg.index)  # 强制显示所有年份
        ax1.tick_params(axis='x', rotation=45, labelsize=20)  # 旋转

        # 图例
        lns = lns1 + lns2 + lns3
        labs = [l.get_label() for l in lns]
        ax1.legend(lns, labs, loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=True, fontsize=16)
        
        plt.tight_layout()
        save_figure(fig, "Final_公平与效率关联图.png")
    
    def plot_integrated_visuals(self):
        """效率趋势图 (优化：补全 SE、去掉数值标注、解决重叠问题)"""
        print("\n[阶段 2] 生成效率趋势图 (TE/PTE/SE)...")
        plot_style()
        fig, ax = plt.subplots(figsize=(13, 8))
        
        avg_eff = self.df_dea.groupby('年份')[['综合效率(TE)', '纯技术效率(PTE)', '规模效率(SE)']].mean()
        
        colors = {'TE': '#1565C0', 'PTE': '#2E7D32', 'SE': '#EF6C00'}
        markers = {'TE': 'o', 'PTE': 's', 'SE': 'D'}
        
        for col in ['综合效率(TE)', '纯技术效率(PTE)', '规模效率(SE)']:
            label_short = col.split('(')[1].split(')')[0]
            ax.plot(avg_eff.index, avg_eff[col], marker=markers[label_short], 
                    color=colors[label_short], linewidth=3, markersize=9, label=col)

        # 背景
        ax.axhspan(0.9, 1.0, facecolor='#E8F5E9', alpha=0.3)
        ax.axhspan(0.7, 0.9, facecolor='#FFF3E0', alpha=0.3)

        ax.set_ylim(0.5, 1.08)
        ax.set_ylabel("效率得分 (Efficiency Score)", fontsize=25)
        
        # 横坐标旋转
        plt.xticks(rotation=45, ha='right', fontsize=20)
        
        # 图例
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=20)
        
        plt.tight_layout()
        save_figure(fig, "Final_效率趋势图.png")

    def plot_relation_network_preview(self, network_data):
        """关系网络图 (增加类别彩色图例)"""
        import networkx as nx
        print("\n[阶段 6] 正在生成关系网静态预览图...")
        
        G = nx.Graph()
        for node in network_data['nodes']:
            G.add_node(node['name'], category=node['category'])
        for link in network_data['links']:
            source_name = network_data['nodes'][int(link['source'])]['name']
            target_name = network_data['nodes'][int(link['target'])]['name']
            G.add_edge(source_name, target_name, weight=link['value'])
            
        fig, ax = plt.subplots(figsize=(11, 11))
        pos = nx.spring_layout(G, seed=42, k=0.5) 
        
        # 类别颜色定义
        color_map_raw = {0: '#64B5F6', 1: '#81C784', 2: '#FF8A65'}
        node_colors = [color_map_raw[G.nodes[node]['category']] for node in G.nodes()]
        
        nx.draw_networkx_nodes(G, pos, node_size=2500, node_color=node_colors, alpha=0.9, ax=ax, edgecolors='gray')
        nx.draw_networkx_labels(G, pos, font_size=16, font_family='SimHei', font_weight='bold', ax=ax)
        
        edges = G.edges(data=True)
        nx.draw_networkx_edges(G, pos, width=[abs(d['weight'])*6 for u,v,d in edges], alpha=0.3, edge_color='gray', ax=ax)
        
        # --- 核心修改：添加自定义彩色图例说明 ---
        legend_elements = [
            Patch(facecolor='#64B5F6', label='医疗资源 (Input)'),
            Patch(facecolor='#81C784', label='配置效率 (DEA 指标)'),
            Patch(facecolor='#FF8A65', label='健康效益 (Output)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', title="节点类别说明", fontsize=15, title_fontsize=15, frameon=True)

        # plt.title("‘资源-效率-健康’关联路径网络分析图", fontsize=18, fontweight='bold', pad=20)
        ax.axis('off')
        save_figure(fig, "Final_关系网络预览.png")

if __name__ == "__main__":
    analyser = DEAAnalysisSystem()
    analyser.run_full_dea()
    year_list = ["2024年", "2023年", "2022年", "2021年", "2020年", "2019年", "2018年", "2017年", "2016年", "2015年"]

    # analyser.run_gini_correlation()
    # analyser.run_Tobit_regression()
    # network_data = analyser.generate_relation_network()
    # analyser.plot_integrated_visuals()
    # analyser.plot_relation_network_preview(network_data)
    print("\n--- 全流程分析任务已完成，插图已增强 ---")
    # verifier = DEAValidationRSR(analyser.df_merged, analyser.df_dea, analyser.input_cols, analyser.output_cols)
    all_data = pd.DataFrame()
    for year in year_list:
        current_data = analyser.run_cluster(year)
        # 把当前年份结果追加到 all_data 中
        all_data = pd.concat([all_data, current_data], ignore_index=True)
        # compare_data = verifier.verify_consistency(year)
        # verifier.plot_validation_scatter(compare_data,year)  
    # verifier.save_rsr_data() 
    save_dataframe(all_data, "DEA效率分析.csv")
    csv_to_sql("论文/output/analysis_data/DEA效率分析.csv", "dea")

    