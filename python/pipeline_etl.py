"""
pipeline_etl.py
-------------------------------------------------------------------------
Motor de Ingeniería de Datos para extracción, validación de Data Quality
y transformación con Pandas.

Autor: Jocelyn Tapia Arancibia
Rol: Data Engineer / Backend Developer
-------------------------------------------------------------------------
"""

import logging
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime

# Configuración del Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

class DataPipelineEngine:
    """
    Clase principal para ejecutar flujos ETL confiables con métricas integradas.
    """
    
    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
        self.logger = logging.getLogger(f"Pipeline-{pipeline_id}")

    def extract(self, raw_records: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convierte datos crudos JSON/Dict en un DataFrame de Pandas."""
        self.logger.info(f"Extrayendo {len(raw_records)} registros de la fuente...")
        return pd.DataFrame(raw_records)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica reglas de negocio, limpieza de cadenas y control de duplicados.
        """
        self.logger.info("Ejecutando reglas de transformación y Data Quality...")
        
        # 1. Normalización de cadenas
        if "nombre" in df.columns:
            df["nombre_clean"] = df["nombre"].str.strip().str.title()
            
        # 2. Casteo seguro de valores numéricos
        if "monto" in df.columns:
            df["monto"] = pd.to_numeric(df["monto"], errors='coerce').fillna(0.0)
            
        # 3. Inyección de Metadata para trazabilidad (Data Lineage)
        df["processed_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
        df["pipeline_id"] = self.pipeline_id
        
        # 4. Deduplicación
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=["tx_id"], keep="first")
        
        self.logger.info(f"Registros deduplicados: {initial_count - len(df_clean)}")
        return df_clean

    def run_pipeline(self, payload: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ejecuta el ciclo ETL completo."""
        try:
            df_raw = self.extract(payload)
            df_transformed = self.transform(df_raw)
            
            return {
                "status": "SUCCESS",
                "processed_records": len(df_transformed),
                "data": df_transformed.to_dict(orient="records")
            }
        except Exception as e:
            self.logger.error(f"Fallo en la ejecución del pipeline: {str(e)}")
            return {"status": "ERROR", "message": str(e)}

# Bloque de ejecución / pruebas unitarias
if __name__ == "__main__":
    sample_data = [
        {"tx_id": "TX101", "nombre": "  jocelyn tapia ", "monto": "2500.00"},
        {"tx_id": "TX101", "nombre": "  jocelyn tapia ", "monto": "2500.00"},  # Duplicado
        {"tx_id": "TX102", "nombre": "carlos ruiz", "monto": "INVALID"}        # Valor corrupto
    ]
    
    engine = DataPipelineEngine(pipeline_id="CEPTINEL-001")
    response = engine.run_pipeline(sample_data)
    print(response)
