"""
Real-Time PEP & Fraud Screening Engine
-------------------------------------------------------------------------
Servicio REST para validación de personas expuestas políticamente (PEP)
y detección de patrón de fraccionamiento ("pitufeo").

Autor: Jocelyn Tapia Arancibia
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from difflib import SequenceMatcher
from datetime import datetime

app = FastAPI(
    title="PEP & Fraud Screening API",
    description="Engine para validación normativa y detección de anomalías transaccionales.",
    version="1.0.0"
)

# Base de Datos simulada en memoria (Listas de Sanciones)
PEP_WATCHLIST = [
    {"id": "PEP-001", "nombre": "Carlos Alberto Ruiz Sandoval", "cargo": "Ex Ministro de Estado", "pais": "CL"},
    {"id": "PEP-002", "nombre": "Juan Pablo Morales Vega", "cargo": "Director de Empresa Pública", "pais": "CL"},
    {"id": "PEP-003", "nombre": "Maria Fernanda Gomez Lopez", "cargo": "Senadora", "pais": "CL"}
]

class TransactionRequest(BaseModel):
    tx_id: str = Field(..., example="TX-99812")
    id_cliente: str = Field(..., example="CLI-4401")
    nombre_cliente: str = Field(..., example="Carlos A. Ruiz S.")
    monto_usd: float = Field(..., gt=0, example=9500.00)
    pais_destino: str = Field(..., example="CL")

class ScreeningResponse(BaseModel):
    tx_id: str
    is_pep_match: bool
    confidence_score: float
    pep_details: Optional[dict] = None
    is_structuring_alert: bool
    timestamp_utc: str

def fuzzy_similarity(a: str, b: str) -> float:
    """Calcula similitud de texto entre dos nombres."""
    return round(SequenceMatcher(None, a.upper(), b.upper()).ratio(), 4)

@app.post("/api/v1/screen", response_model=ScreeningResponse, status_code=status.HTTP_200_OK)
def screen_transaction(payload: TransactionRequest):
    best_match = None
    highest_score = 0.0
    UMBRAL_CORRESPONDENCIA = 0.75
    UMBRAL_PITUFEO = 9000.00  # Operaciones cercanas al límite normativo (10k USD)

    # 1. Matching Difuso contra Lista PEP
    for pep in PEP_WATCHLIST:
        score = fuzzy_similarity(payload.nombre_cliente, pep["nombre"])
        if score > highest_score:
            highest_score = score
            best_match = pep

    is_pep = highest_score >= UMBRAL_CORRESPONDENCIA
    
    # 2. Regla de Detección de Fraccionamiento (Structuring/Pitufeo)
    is_structuring = (9000.0 <= payload.monto_usd < 10000.0)

    return ScreeningResponse(
        tx_id=payload.tx_id,
        is_pep_match=is_pep,
        confidence_score=highest_score,
        pep_details=best_match if is_pep else None,
        is_structuring_alert=is_structuring,
        timestamp_utc=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
