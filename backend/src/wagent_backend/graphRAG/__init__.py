"""graphRAG —— 知识图谱核心：本体定义、Neo4j 存储层、种子数据。

对外只暴露三个模块：
    schema  本体常量 + 实体/关系 pydantic 模型
    store   Neo4jGraph（对 Neo4j 的封装，全部查询接口）
    seed    设备登记表种子数据装载
"""
