from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import equipment, sensors, alerts, recommendations, trends, auth
from app.auth import get_current_user
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

protected = [Depends(get_current_user)]

# Public — no token required to log in
app.include_router(auth.router)

# Everything else requires a valid bearer token
app.include_router(equipment.router, dependencies=protected)
app.include_router(sensors.router, dependencies=protected)
app.include_router(alerts.router, dependencies=protected)
app.include_router(recommendations.router, dependencies=protected)
app.include_router(trends.router, dependencies=protected)

@app.get("/")
def root():
    return {"message": "Digital Twin Pump API is running"}