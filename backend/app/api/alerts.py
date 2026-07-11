from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.models import Alert
from app.schemas.schemas import AlertResponse
from typing import List

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/{equipment_id}", response_model=List[AlertResponse])
def get_alerts(equipment_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Alert)
        .filter(Alert.equipment_id == equipment_id)
        .order_by(desc(Alert.created_at))
        .all()
    )

@router.get("/{equipment_id}/active", response_model=List[AlertResponse])
def get_active_alerts(equipment_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Alert)
        .filter(Alert.equipment_id == equipment_id, Alert.is_resolved == False)
        .order_by(desc(Alert.created_at))
        .all()
    )

@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return {"error": "Alert not found"}
    alert.is_resolved = True
    db.commit()
    return {"message": f"Alert {alert_id} resolved"}