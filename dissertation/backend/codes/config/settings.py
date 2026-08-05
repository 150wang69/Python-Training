#配置数据库信息
mysql_config = {
    "host": "localhost", #mysql主机名，本地默认
    "port": 3306, #默认端口
    "user": "root",
    "password": "wy200469",
    "db": "essay_dataset",
    "charset": "utf8mb4" #防止中文乱码
}

#配置模型参数
model_params = {
    "gini_threshold": 0.4, #基尼系数不均衡阈值
    'dea_model_type': 'input_oriented', #DEA投入导向（投入-》效益分析）
    'dea_return_to_scale': 'CRS', #规则报酬不变
    'cluster_best_k': 4, #聚类最优类别数（发展模式数）
    'network_corr_threshold': 0.3 #关系网强关联阈值(|r|>0.3)
}

#输出路径，不在这里做统一管理

