#!/usr/bin/env python3
import os
import json
import asyncio
import tempfile
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from expert_system import ExpertSystem
from vision.inferencia import predecir_morfologia

app = FastAPI(
    title="SEADD Backend Server",
    description="Servidor de inferencia y dashboard para el Sistema Experto Diagnóstico Dermatológico con WebSockets.",
    version="1.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia del Sistema Experto
expert_system = ExpertSystem()

# Gestor de Conexiones WebSocket (Reverse Tunneling)
class ConnectionManager:
    def __init__(self):
        self.rapiro_ws: Optional[WebSocket] = None
        self.dashboard_wss: List[WebSocket] = []

    async def connect_rapiro(self, websocket: WebSocket):
        await websocket.accept()
        self.rapiro_ws = websocket

    def disconnect_rapiro(self):
        self.rapiro_ws = None

    async def connect_dashboard(self, websocket: WebSocket):
        await websocket.accept()
        self.dashboard_wss.append(websocket)

    def disconnect_dashboard(self, websocket: WebSocket):
        if websocket in self.dashboard_wss:
            self.dashboard_wss.remove(websocket)

    async def send_to_rapiro(self, message: dict):
        """Envía un comando JSON al robot Rapiro."""
        if self.rapiro_ws:
            try:
                await self.rapiro_ws.send_json(message)
            except Exception:
                self.rapiro_ws = None

    async def broadcast_to_dashboards(self, message: Any, is_binary: bool = False):
        """Retransmite datos (JSON o binario de cámara) a todos los dashboards conectados."""
        for ws in self.dashboard_wss:
            try:
                if is_binary:
                    await ws.send_bytes(message)
                else:
                    await ws.send_json(message)
            except Exception:
                self.dashboard_wss.remove(ws)

manager = ConnectionManager()

# Modelos de Pydantic
class SymptomInput(BaseModel):
    location: str
    morphology: str
    color: str
    pruritus: float
    duration: float
    stress: bool


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
    """Ejecuta la inferencia experta y cambia el estado de los LEDs del robot."""
    # Notificar estado al robot
    await manager.send_to_rapiro({"type": "state", "value": "inferring"})
    
    try:
        result = expert_system.infer(
            location=inputs.location,
            morphology=inputs.morphology,
            color=inputs.color,
            pruritus=inputs.pruritus,
            duration=inputs.duration,
            stress=inputs.stress
        )
        # Inferencia completada con éxito
        await manager.send_to_rapiro({"type": "state", "value": "result_ready"})
        return JSONResponse(content=result)
    except Exception as e:
        # Revertir a espera en caso de error
        await manager.send_to_rapiro({"type": "state", "value": "waiting"})
        return JSONResponse(status_code=500, content={"ok": False, "message": str(e)})

@app.post("/api/predict")
async def predict(image: UploadFile = File(...)):
    """Clasifica la morfología de una lesión cutánea a partir de una imagen."""
    # Notificar estado de captura (gesto de pulgar arriba en Rapiro)
    await manager.send_to_rapiro({"type": "state", "value": "capturing"})
    # Dar tiempo a que el robot realice el gesto
    await asyncio.sleep(1.5)
    
    # Cambiar a estado de análisis
    await manager.send_to_rapiro({"type": "state", "value": "analyzing"})

    import time
    import tensorflow as tf
    import traceback
    tmp_path = None
    try:
        suffix = os.path.splitext(image.filename or "")[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await image.read())
            tmp_path = tmp.name

        t0 = time.perf_counter()
        prediction = await asyncio.to_thread(predecir_morfologia, tmp_path)
        elapsed = time.perf_counter() - t0

        gpus = tf.config.list_physical_devices('GPU')
        device = "GPU (CUDA)" if len(gpus) > 0 else "CPU (TensorFlow)"
        file_size_kb = round(os.path.getsize(tmp_path) / 1024, 1)

        await manager.send_to_rapiro({"type": "state", "value": "waiting"})
        return JSONResponse(content={
            "ok": True, 
            "prediction": prediction,
            "stats": {
                "inference_time_ms": round(elapsed * 1000, 1),
                "file_size_kb": file_size_kb,
                "device": device
            }
        })
    except Exception as e:
        traceback.print_exc()
        await manager.send_to_rapiro({"type": "state", "value": "waiting"})
        return JSONResponse(status_code=400, content={"ok": False, "error": str(e)})
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "SEADD Backend is running."}

# --- ENDPOINTS WEBSOCKET (TÚNEL REVERSO) ---

@app.websocket("/ws/rapiro")
async def websocket_rapiro(websocket: WebSocket):
    """Canal persistente para la Raspberry Pi (envía cámara y telemetría, recibe comandos)."""
    await manager.connect_rapiro(websocket)
    print("Conexión WebSocket establecida con Rapiro.")
    # Notificar a los dashboards
    await manager.broadcast_to_dashboards({"type": "rapiro_status", "connected": True})
    
    try:
        while True:
            # Rapiro puede enviar imágenes (binario) o telemetría (texto)
            message = await websocket.receive()
            if "bytes" in message:
                # Transmitir el frame de video a los dashboards
                await manager.broadcast_to_dashboards(message["bytes"], is_binary=True)
            elif "text" in message:
                data = json.loads(message["text"])
                await manager.broadcast_to_dashboards(data)
    except WebSocketDisconnect:
        manager.disconnect_rapiro()
        print("Conexión WebSocket con Rapiro cerrada.")
        await manager.broadcast_to_dashboards({"type": "rapiro_status", "connected": False})

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """Canal para el navegador del médico (recibe cámara, envía acciones del robot)."""
    await manager.connect_dashboard(websocket)
    # Enviar estado actual de Rapiro al conectar
    is_connected = manager.rapiro_ws is not None
    await websocket.send_json({"type": "rapiro_status", "connected": is_connected})
    
    try:
        while True:
            data = await websocket.receive_json()
            # Si el médico ejecuta un comando en el dashboard, se encamina a Rapiro
            await manager.send_to_rapiro(data)
    except WebSocketDisconnect:
        manager.disconnect_dashboard(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
