from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import equipment, sensors, alerts

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Digital Twin Pump API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(equipment.router)
app.include_router(sensors.router)
app.include_router(alerts.router)

@app.get("/")
def root():
    return {"message": "Digital Twin Pump API is running"}

