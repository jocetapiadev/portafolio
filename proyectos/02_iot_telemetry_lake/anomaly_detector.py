"""
IoT Telemetry Anomaly Detector
-------------------------------------------------------------------------
Procesador de eventos de telemetría de flotas viales/mineras para
detección de excesos de velocidad y consumo anómalo de combustible.

Autor: Jocelyn Tapia Arancibia
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List

logger = logging.getLogger("TelemetryProcessor")
logger.setLevel(logging.INFO)

class TelemetryAnomalyDetector:
    def __init__(self, max_speed_limit: float = 100.0, z_score_threshold: float = 2.5):
        self.max_speed_limit = max_speed_limit
        self.z_score_threshold = z_score_threshold

    def process_telemetry_batch(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Procesa lote de sensores de flota e identifica anomalías térmicas y de velocidad."""
        if not events:
            return {"status": "EMPTY_BATCH", "alerts": []}

        df = pd.DataFrame(events)

        # 1. Filtro por exeso de velocidad
        excess_speed_df = df[df["speed_kmh"] > self.max_speed_limit]

        # 2. Anomaly Detection estadístico para consumo de combustible (Z-Score)
        if len(df) > 3 and "fuel_consumption_lph" in df.columns:
            mean_fuel = df["fuel_consumption_lph"].mean()
            std_fuel = df["fuel_consumption_lph"].std()
            
            if std_fuel > 0:
                df["fuel_zscore"] = (df["fuel_consumption_lph"] - mean_fuel) / std_fuel
                anomalous_fuel_df = df[df["fuel_zscore"].abs() > self.z_score_threshold]
            else:
                anomalous_fuel_df = pd.DataFrame()
        else:
            anomalous_fuel_df = pd.DataFrame()

        alerts = []
        
        # Generar Alertas de Velocidad
        for _, row in excess_speed_df.iterrows():
            alerts.append({
                "vehicle_id": row["vehicle_id"],
                "type": "EXCESS_SPEED",
                "val": row["speed_kmh"],
                "limit": self.max_speed_limit,
                "timestamp": row.get("timestamp")
            })

        # Generar Alertas de Combustible
        for _, row in anomalous_fuel_df.iterrows():
            alerts.append({
                "vehicle_id": row["vehicle_id"],
                "type": "ANOMALOUS_FUEL_CONSUMPTION",
                "val": row["fuel_consumption_lph"],
                "z_score": round(row["fuel_zscore"], 2),
                "timestamp": row.get("timestamp")
            })

        return {
            "status": "PROCESSED",
            "total_records": len(df),
            "total_alerts": len(alerts),
            "alerts": alerts
        }

# Simulación de AWS Lambda Handler
def lambda_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    detector = TelemetryAnomalyDetector(max_speed_limit=90.0)
    records = event.get("records", [])
    result = detector.process_telemetry_batch(records)
    return {"statusCode": 200, "body": result}

if __name__ == "__main__":
    sample_event = {
        "records": [
            {"vehicle_id": "MIG-01", "speed_kmh": 85.5, "fuel_consumption_lph": 12.0, "timestamp": "2026-08-12T10:00:00Z"},
            {"vehicle_id": "MIG-02", "speed_kmh": 115.0, "fuel_consumption_lph": 13.5, "timestamp": "2026-08-12T10:00:05Z"}, # Alerta Velocidad
            {"vehicle_id": "MIG-03", "speed_kmh": 70.0, "fuel_consumption_lph": 48.0, "timestamp": "2026-08-12T10:00:10Z"}, # Alerta Combustible
        ]
    }
    print(lambda_handler(sample_event))
