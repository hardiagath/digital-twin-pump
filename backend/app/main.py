from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import equipment, sensors, alerts, recommendations, trends
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Digital Twin Pump API")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(equipment.router)
app.include_router(sensors.router)
app.include_router(alerts.router)
app.include_router(recommendations.router)
app.include_router(trends.router)

@app.get("/")
def root():
    return {"message": "Digital Twin Pump API is running"}