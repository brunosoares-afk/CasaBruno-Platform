from fastapi import FastAPI
from app.routers.system import router as system_router
from app.routers.homeassistant import router as homeassistant_router
from app.routers.mikrotik import router as mikrotik_router
from app.routers.docker import router as docker_router
from app.routers.network import router as network_router
from app.routers.scenes import router as scenes_router
from app.routers.fred import router as fred_router
from app.routers.alexa import router as alexa_router
from app.api.kernel import router as kernel_router
from app.api.application import router as application_router
from app.api.bootstrap import router as bootstrap_router
from app.api.config import router as config_router
from app.api.storage import router as storage_router
from app.api.database import router as database_router
from app.api.models import router as models_router
from app.api.services import router as services_router
from app.api.plugins import router as plugins_router
from app.api.events import router as events_router
from app.api.tuya import router as tuya_router
from app.integrations.android.routes import router as android_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
app = FastAPI(
    title="CasaBruno Platform",
    version="2.0.0",
    description="CasaBruno Platform API"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {
        "name": "CasaBruno Platform",
        "version": "2.0.0",
        "status": "online"
    }
@app.get("/health")
def health():
    return {
        "status": "online"
    }
# Routers principais
app.include_router(system_router)
app.include_router(homeassistant_router)
# Core
app.include_router(kernel_router)
app.include_router(application_router)
app.include_router(bootstrap_router)
app.include_router(config_router)
app.include_router(storage_router)
app.include_router(database_router)
app.include_router(models_router)
app.include_router(services_router)
app.include_router(plugins_router)
app.include_router(events_router)
app.include_router(tuya_router)
app.include_router(mikrotik_router)
app.include_router(docker_router)
app.include_router(network_router)
app.include_router(scenes_router)
app.include_router(fred_router)
app.include_router(alexa_router)
app.mount("/alexa/audio", StaticFiles(directory="/opt/CasaBruno-Platform/backend/tts_audio"), name="alexa_audio")
app.include_router(android_router)
