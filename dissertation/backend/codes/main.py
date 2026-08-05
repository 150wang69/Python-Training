import os
import sys
import json
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional

# 环境路径配置
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir)) 

from utils.common import load_sqldata

app = FastAPI(title="基于DEA的地区医疗投入和健康效益关联性数据结果展示")

# 配置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件路径
RELATION_NETWORK_PATH = 'e:/VSCodeFiles/论文/output/analysis_data/relation_network.json'
FIGURES_DIR = 'e:/VSCodeFiles/论文/output/figures'

if os.path.exists(FIGURES_DIR):
    app.mount("/figures", StaticFiles(directory=FIGURES_DIR), name="figures")

# --- 工具方法 ---
def clean_data(val):
    """处理数据库中的空值或异常值，确保返回给前端的是 JSON 兼容的数值"""
    try:
        if pd.isna(val) or val is None:
            return 0.0
        return float(val)
    except:
        return 0.0

#1 中国地图数据 获取TE
@app.get("/api/map_data")
async def get_map_data(year: str):
    try:
        sql = f"SELECT 地区, `综合效率(TE)` FROM dea WHERE 年份 = '{year}'"
        df = load_sqldata(sql)
        if df is None or df.empty:
            return {"year": year, "data": []}
        
        res = [{"name": row['地区'], "value": clean_data(row['综合效率(TE)'])} for _, row in df.iterrows()]
        return {"year": year, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"地图数据查询异常: {str(e)}")

#2 地区数据详情 显示投入产出数据和DEA数据
@app.get("/api/region_detail/{region_name}")
async def get_region_detail(year: str, region_name: str):
    try:
        # 查询 DEA 表获取效率和冗余
        sql_d = f"SELECT * FROM dea WHERE 地区 = '{region_name}' AND 年份 = '{year}'"
        df_d = load_sqldata(sql_d)
        print(df_d)

        if df_d is None or df_d.empty:
            raise HTTPException(status_code=404, detail="未找到该地区该年份数据")

        dd = df_d.iloc[0]

        # 构造前端 detail-chart 所需的数据
        return {
            "region": region_name,
            "year": year,
            "efficiency_metrics": {
                "labels": ["综合效率", "纯技术效率", "规模效率"],
                "values": [clean_data(dd['综合效率(TE)']), clean_data(dd['纯技术效率(PTE)']), clean_data(dd['规模效率(SE)'])]
            },
             "waste_analysis": {
                "redundancy": {
                    "labels": ["财政冗余", "机构冗余", "人员冗余"], 
                    "values": [
                        clean_data(dd['冗余_财政(亿元)']),
                        clean_data(dd['冗余_机构(个)']),
                        clean_data(dd["冗余_人员(人)"])
                    ]
                },
                "deficit": {
                    "labels": ["病床利用率不足", "健康效益不足", ], 
                    "values": [
                        clean_data(dd.get('不足_利用率(%)', 0)),
                        clean_data(dd.get('不足_健康效益', 0))
                    ]
                }
             }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# #3 年度基尼系数详情
@app.get("/api/gini_data")
async def get_gini_data(year: str):
    try:
        # 兼容处理年份后缀
        query_year = year if "年" in year else f"{year}年"
        
        df = load_sqldata(f"SELECT * FROM gini WHERE 年份 = '{query_year}'")
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="未找到该年份基尼系数数据")

        # 定义 7 个指标的中文名映射 (总量 + 人均)
        resource_names = {
            '地方财政医疗卫生支出(亿元)': '财政卫生支出(总量)',
            '医疗卫生机构床位数(万张)': '床位数(总量)',
            '医疗卫生机构数(个)': '机构数(总量)',
            '人均财政卫生支出(元)': '财政卫生支出(人均)',
            '每万人医疗卫生机构床位数(张)': '床位数(每万人)',
            '每万人医疗卫生机构数(个)': '机构数(每万人)',
            '每万人拥有卫生技术人员数(人)': '技术人员(每万人)'
        }

        categories = []
        values = []
        statuses = []

        row = df.iloc[0]
        # 遍历所有 7 个列
        for col, friendly_name in resource_names.items():
            if col in df.columns:
                categories.append(friendly_name)
                # 获取数值
                val = row[col]
                values.append(float(val) if val is not None else 0.0)
                # 获取状态字段，例如：地方财政医疗卫生支出(亿元)_状态
                status_col = f"{col}_状态"
                status_val = row.get(status_col, "正常") # 如果没找到状态字段，默认显示正常
                statuses.append(status_val)

        return {
            "year": query_year,
            "chart_data": {
                "categories": categories,
                "values": values,
                "statuses": statuses
            }
        }
    except Exception as e:
        print(f"Gini数据接口报错: {e}")
        raise HTTPException(status_code=500, detail=str(e))
#4 总量和人均基尼系数数据
@app.get("/api/gini_trend")
async def get_gini_trend(indicator: str):
    try:
        # 查询所有年份的该指标
        df = load_sqldata(f"SELECT 年份, `{indicator}` FROM gini ORDER BY 年份 ASC")
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="趋势数据缺失")

        return {
            "indicator": indicator,
            "years": df['年份'].astype(str).tolist(),
            "values": [clean_data(v) for v in df[indicator]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 弃用 接口 5: 宏观背景 (卫生总费用 & 预期寿命) ---
@app.get("/api/macro_background")
async def get_macro_background():
    try:
        # 全国卫生总费用
        df_cost = load_sqldata("SELECT 年份, `卫生总费用(亿元)`, `人均卫生费用(元)` FROM total_cost ORDER BY 年份 ASC")
        # 预期寿命 (1990, 2000, 2010, 2020)
        df_long = load_sqldata("SELECT 年份, `平均预期寿命(岁)` FROM longevity ORDER BY 年份 ASC")
        
        return {
            "cost_trend": {
                "years": df_cost['年份'].tolist() if df_cost is not None else [],
                "total": [clean_data(v) for v in df_cost['卫生总费用(亿元)']] if df_cost is not None else [],
                "per_capita": [clean_data(v) for v in df_cost['人均卫生费用(元)']] if df_cost is not None else []
            },
            "longevity": {
                "years": df_long['年份'].tolist() if df_long is not None else [],
                "values": [clean_data(v) for v in df_long['平均预期寿命(岁)']] if df_long is not None else []
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#5 关系网数据接口
@app.get("/api/relation_network")
async def get_relation_network():
    if not os.path.exists(RELATION_NETWORK_PATH):
        raise HTTPException(status_code=404, detail="关系网文件缺失")
    try:
        with open(RELATION_NETWORK_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#6 十年DEA效率数据
@app.get("/api/dea_trend_data")
async def get_dea_trend_data():
    try:
        # 查询 2015-2024 年的数据
        years = [f"{y}年" for y in range(2015, 2025)]
        year_str = "','".join(years)
        
        # 按年份分组，计算全国平均效率
        sql = f"""
            SELECT 年份, 
                   AVG(`综合效率(TE)`) as te, 
                   AVG(`纯技术效率(PTE)`) as pte, 
                   AVG(`规模效率(SE)`) as se 
            FROM dea 
            WHERE 年份 IN ('{year_str}')
            GROUP BY 年份 
            ORDER BY 年份 ASC
        """
        df = load_sqldata(sql)
        
        if df is None or df.empty:
            return {"years": years, "te": [], "pte": [], "se": []}

        return {
            "years": df['年份'].tolist(),
            "te": [round(clean_data(v), 3) for v in df['te']],
            "pte": [round(clean_data(v), 3) for v in df['pte']],
            "se": [round(clean_data(v), 3) for v in df['se']]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

#7 聚类分析接口 直接从数据库读取预计算结果) ---
# --- 7 聚类分析接口 (严格对齐你的数据库字段) ---
@app.get("/api/cluster_data")
async def get_cluster_data(year: str):
    try:
        # 注意：字段名必须加反引号，因为含有括号
        sql = f"SELECT `地区`, `纯技术效率(PTE)`, `规模效率(SE)`, `类别` FROM dea WHERE 年份 = '{year}'"
        df = load_sqldata(sql)
        
        if df is None or df.empty:
            return []

        res = []
        for _, row in df.iterrows():
            res.append({
                "name": row['地区'],
                # 这里的 value[0] 是 X 轴 (PTE)，value[1] 是 Y 轴 (SE)
                "value": [
                    float(row['纯技术效率(PTE)']), 
                    float(row['规模效率(SE)'])
                ],
                "cluster_name": row['类别']  # 这里就是你数据库里的“中水平地区...”等字符串
            })
        return res
    except Exception as e:
        print(f"聚类接口报错: {e}")
        raise HTTPException(status_code=500, detail="获取聚类数据失败")

#8 公平与效率综合分析接口
@app.get("/api/gini_dea_coupling")
async def get_gini_dea_coupling():
    try:
        # 获取基尼系数的三种均值
        df_gini = load_sqldata("SELECT 年份, `总量基尼均值`, `人均基尼均值` FROM gini ORDER BY 年份 ASC")
        
        # 获取全国 DEA 平均综合效率
        df_dea = load_sqldata("""
            SELECT 年份, AVG(`综合效率(TE)`) as avg_te 
            FROM dea 
            GROUP BY 年份 
            ORDER BY 年份 ASC
        """)

        return {
            "years": df_gini['年份'].tolist(),
            "gini_total": [round(float(v), 3) for v in df_gini['总量基尼均值']],
            "gini_per": [round(float(v), 3) for v in df_gini['人均基尼均值']],
            "dea_values": [round(float(v), 3) for v in df_dea['avg_te']]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#9 获取 RSR 与 DEA 相关性验证数据
@app.get("/api/rsr_validation")
async def get_rsr_validation(year: str):
    try:
        # 从 rsr 数据表中查询
        sql = f"SELECT `地区`, `综合效率(TE)`, `RSR得分`, `Spearman相关系数`, `P值`, `相关性` FROM rsr WHERE 年份 = '{year}'"
        df = load_sqldata(sql)
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"未找到 {year} 的验证数据")

        # 提取全局统计结论 (取第一行)
        summary = {
            "correlation": clean_data(df['Spearman相关系数'].iloc[0]),
            "p_value": clean_data(df['P值'].iloc[0]),
            "status": str(df['相关性'].iloc[0])
        }

        # 构造散点坐标 [x, y, name]
        points = []
        for _, row in df.iterrows():
            points.append({
                "name": row['地区'],
                "value": [round(clean_data(row['RSR得分']), 4), round(clean_data(row['综合效率(TE)']), 4)]
            })

        return {
            "year": year,
            "summary": summary,
            "points": points
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)