"""
FastAPI — Liga Predictor API

Endpoints:
  GET  /api/info      → Informação sobre o dataset (equipas, jornadas, etc.)
  POST /api/simulate  → Executa a simulação Monte Carlo
  GET  /              → Serve o frontend (index.html)
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import os

from app.monte_carlo import run_simulation, get_info

# --- App Setup ---
app = FastAPI(
    title="Liga Predictor",
    description="API de Simulação Monte Carlo para a Primeira Liga Portuguesa",
    version="1.0.0"
)

# Servir ficheiros estáticos (CSS, JS, imagens)
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# --- Models ---
class SimulationRequest(BaseModel):
    jornada: int = Field(default=17, ge=1, le=34, description="Jornada a partir da qual simular")
    num_simulacoes: int = Field(default=1000, ge=100, le=10000, description="Número de iterações Monte Carlo")
    epoca: str = Field(default="2023-2024", description="Época a simular")


# --- Routes ---
@app.get("/")
async def serve_frontend():
    """Serve a página principal da aplicação."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/info")
async def api_info():
    """Retorna informação sobre os dados disponíveis."""
    try:
        info = get_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/simulate")
async def api_simulate(request: SimulationRequest):
    """Executa a simulação Monte Carlo e retorna os resultados."""
    try:
        result = run_simulation(
            jornada_alvo=request.jornada,
            num_simulacoes=request.num_simulacoes,
            epoca_alvo=request.epoca
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na simulação: {str(e)}")
