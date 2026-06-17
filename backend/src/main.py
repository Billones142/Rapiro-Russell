import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from expert_system import ExpertSystem

app = FastAPI(
    title="SEADD Backend Server",
    description="Servidor de inferencia y dashboard para el Sistema Experto Diagnóstico Dermatológico.",
    version="1.0.0"
)

# Configurar CORS para permitir comunicación desde cualquier origen (e.g. Raspberry Pi o interfaz de desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia del Sistema Experto
expert_system = ExpertSystem()

# Modelos de Pydantic
class SymptomInput(BaseModel):
    location: str
    morphology: str
    color: str
    pruritus: float
    duration: float
    stress: bool

class VisionStubResponse(BaseModel):
    morphology: str
    color: str
    confidence: float

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Sirve la página del Dashboard del Médico."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")
    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="Dashboard template not found")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content

@app.post("/api/infer")
async def run_inference(inputs: SymptomInput):
    """Ejecuta la inferencia experta con el motor híbrido."""
    try:
        result = expert_system.infer(
            location=inputs.location,
            morphology=inputs.morphology,
            color=inputs.color,
            pruritus=inputs.pruritus,
            duration=inputs.duration,
            stress=inputs.stress
        )
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "message": str(e)})

@app.post("/api/vision/stub", response_model=VisionStubResponse)
async def vision_stub(request: Request):
    """
    Stub temporal para el modelo de visión.
    Simula la clasificación de morfología y color con sus niveles de confianza.
    """
    # En el futuro, este endpoint procesará una imagen binaria recibida.
    # Por ahora, simulamos una detección de alta confianza para integrar el flujo.
    return {
        "morphology": "escama",
        "color": "blanco nacarado",
        "confidence": 0.92
    }

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "SEADD Backend is running."}

if __name__ == "__main__":
    import uvicorn
    # Ejecuta en puerto 8000 por defecto
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

