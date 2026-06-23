"""
医疗数据加载器 - 管理和加载868条专业医疗数据
数据包括: 599条药品说明书 + 92条中医共识 + 45条中成药 + 132条中西医指南
"""
import pandas as pd
import os
from pathlib import Path

class MedicalDataLoader:
    """医疗数据加载器 - 单例模式"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MedicalDataLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.medicine_manuals = None
        self.tcm_consensus = None
        self.patent_medicine = None
        self.integrated_medicine = None

        self._load_all_data()
        self._initialized = True

    def _load_all_data(self):
        """加载所有医疗数据"""
        print("[INFO] 正在加载医疗数据...")

        # 数据文件路径
        base_path = Path("./data")

        # 1. 加载药品说明书 (599条)
        medicine_file = base_path / "extracted_manuals.csv"
        if medicine_file.exists():
            print(f"  [LOAD] 药品说明书: {medicine_file}")
            try:
                self.medicine_manuals = pd.read_csv(medicine_file, encoding='utf-8')
                print(f"  [OK] 成功加载 {len(self.medicine_manuals)} 条药品记录")
            except Exception as e:
                print(f"  [ERROR] 药品数据加载失败: {e}")
        else:
            print(f"  [WARN] 药品文件不存在: {medicine_file}")

        # 2. 加载中医专家共识 (92条)
        tcm_file = base_path / "中医_专家共识_诊疗指南6.17.csv"
        if tcm_file.exists():
            print(f"  [LOAD] 中医专家共识: {tcm_file}")
            try:
                self.tcm_consensus = pd.read_csv(tcm_file, encoding='utf-8')
                print(f"  [OK] 成功加载 {len(self.tcm_consensus)} 条中医专家共识记录")
            except Exception as e:
                print(f"  [ERROR] 中医共识加载失败: {e}")
        else:
            print(f"  [WARN] 中医共识文件不存在: {tcm_file}")

        # 3. 加载中成药数据 (45条)
        patent_file = base_path / "中成药V6.17.csv"
        if patent_file.exists():
            print(f"  [LOAD] 中成药数据: {patent_file}")
            try:
                self.patent_medicine = pd.read_csv(patent_file, encoding='utf-8')
                print(f"  [OK] 成功加载 {len(self.patent_medicine)} 条中成药记录")
            except Exception as e:
                print(f"  [ERROR] 中成药数据加载失败: {e}")
        else:
            print(f"  [WARN] 中成药文件不存在: {patent_file}")

        # 4. 加载中西医指南 (132条)
        integrated_file = base_path / "中西医V6.17.csv"
        if integrated_file.exists():
            print(f"  [LOAD] 中西医指南: {integrated_file}")
            try:
                self.integrated_medicine = pd.read_csv(integrated_file, encoding='utf-8')
                print(f"  [OK] 成功加载 {len(self.integrated_medicine)} 条中西医记录")
            except Exception as e:
                print(f"  [ERROR] 中西医指南加载失败: {e}")
        else:
            print(f"  [WARN] 中西医文件不存在: {integrated_file}")

        print("[SUCCESS] 医疗数据集加载完成")

        # 数据摘要
        print(f"[数据集摘要]")
        if self.medicine_manuals is not None:
            print(f"  药品说明书: {len(self.medicine_manuals)} 条")
        if self.tcm_consensus is not None:
            print(f"  中医专家共识: {len(self.tcm_consensus)} 条")
        if self.patent_medicine is not None:
            print(f"  中成药数据: {len(self.patent_medicine)} 条")
        if self.integrated_medicine is not None:
            print(f"  中西医指南: {len(self.integrated_medicine)} 条")

    def get_medicine_by_name(self, medicine_name: str) -> dict:
        """
        根据药品名称查询详细信息

        参数:
            medicine_name: 药品名称

        返回:
            {
                "found": True/False,
                "medicine": {...药品数据}
            }
        """
        if self.medicine_manuals is None:
            return {"found": False, "error": "药品数据未加载"}

        # 查找药品
        results = self.medicine_manuals[
            self.medicine_manuals['药品名称'].astype(str).str.contains(medicine_name, na=False)
        ]

        if len(results) > 0:
            medicine = results.iloc[0].to_dict()
            return {"found": True, "medicine": medicine}
        else:
            return {"found": False, "error": "药品未找到"}

    def get_tcm_consensus_by_disease(self, disease: str) -> list:
        """
        根据疾病名称查询中医专家共识

        参数:
            disease: 疾病名称

        返回:
            [指南1, 指南2, ...]
        """
        if self.tcm_consensus is None:
            return []

        # 查找相关指南
        results = self.tcm_consensus[
            self.tcm_consensus['病名'].astype(str).str.contains(disease, na=False)
        ]

        if len(results) > 0:
            return results.to_dict('records')
        else:
            return []

    def get_integrated_medicine_by_disease(self, disease: str) -> list:
        """
        根据疾病名称查询中西医指南

        参数:
            disease: 疾病名称

        返回:
            [指南1, 指南2, ...]
        """
        if self.integrated_medicine is None:
            return []

        # 查找相关指南
        results = self.integrated_medicine[
            self.integrated_medicine['疾病'].astype(str).str.contains(disease, na=False)
        ]

        if len(results) > 0:
            return results.to_dict('records')
        else:
            return []

    def get_patent_medicine_by_name(self, medicine_name: str) -> dict:
        """
        根据中成药名称查询信息

        参数:
            medicine_name: 中成药名称

        返回:
            {
                "found": True/False,
                "medicine": {...中成药数据}
            }
        """
        if self.patent_medicine is None:
            return {"found": False, "error": "中成药数据未加载"}

        results = self.patent_medicine[
            self.patent_medicine['药品名称'].astype(str).str.contains(medicine_name, na=False)
        ]

        if len(results) > 0:
            medicine = results.iloc[0].to_dict()
            return {"found": True, "medicine": medicine}
        else:
            return {"found": False, "error": "中成药未找到"}

# 全局实例
_data_loader_instance = None

def get_data_loader() -> MedicalDataLoader:
    """获取数据加载器实例（单例）"""
    global _data_loader_instance
    if _data_loader_instance is None:
        _data_loader_instance = MedicalDataLoader()
    return _data_loader_instance