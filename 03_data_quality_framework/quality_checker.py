"""
Data Quality & Lineage Checker Framework
-------------------------------------------------------------------------
Herramienta para evaluación de calidad de datos y generación de reportes
de salud de tablas antes de la ingesta en Data Warehouses (BigQuery/PostgreSQL).

Autor: Jocelyn Tapia Arancibia
"""

import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

class DataQualityChecker:
    def __init__(self, df: pd.DataFrame, dataset_name: str):
        self.df = df
        self.dataset_name = dataset_name
        self.results = []

    def check_not_null(self, columns: List[str]) -> "DataQualityChecker":
        """Valida que las columnas clave no contengan valores nulos."""
        for col in columns:
            if col in self.df.columns:
                null_count = int(self.df[col].isnull().sum())
                null_ratio = round(null_count / len(self.df), 4) if len(self.df) > 0 else 0
                passed = null_count == 0
                self.results.append({
                    "check": "NOT_NULL",
                    "column": col,
                    "passed": passed,
                    "metrics": {"null_count": null_count, "null_ratio": null_ratio}
                })
        return self

    def check_uniqueness(self, columns: List[str]) -> "DataQualityChecker":
        """Valida la unicidad de las llaves primarias."""
        for col in columns:
            if col in self.df.columns:
                duplicate_count = int(self.df.duplicated(subset=[col]).sum())
                passed = duplicate_count == 0
                self.results.append({
                    "check": "UNIQUE_KEY",
                    "column": col,
                    "passed": passed,
                    "metrics": {"duplicate_count": duplicate_count}
                })
        return self

    def get_summary_report(self) -> Dict[str, Any]:
        """Genera el reporte consolidado de auditoría de datos."""
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r["passed"])
        quality_score = round((passed_checks / total_checks) * 100, 2) if total_checks > 0 else 0.0

        return {
            "dataset": self.dataset_name,
            "timestamp_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"),
            "total_rows": len(self.df),
            "quality_score": quality_score,
            "overall_status": "PASSED" if quality_score == 100.0 else "WARNING",
            "details": self.results
        }

if __name__ == "__main__":
    raw_data = pd.DataFrame([
        {"client_id": "C01", "email": "ana@test.com", "monto": 100},
        {"client_id": "C02", "email": None, "monto": 250},             # Error: Nulo
        {"client_id": "C01", "email": "duplicado@test.com", "monto": 50} # Error: Duplicado
    ])

    dq = DataQualityChecker(raw_data, dataset_name="STG_CLIENTES_DIARIOS")
    report = dq.check_not_null(["client_id", "email"]).check_uniqueness(["client_id"]).get_summary_report()
    
    print(report)
