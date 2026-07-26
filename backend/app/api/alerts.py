from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database import get_db
from app.models.models import Alert, Equipment
from app.schemas.schemas import AlertResponse
from app.services.risk_service import get_equipment_status
from typing import List, Optional

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=List[AlertResponse])
def get_all_alerts(
    risk_level: Optional[str] = Query(default=None),
    resolved:   Optional[bool] = Query(default=None),
    limit:      int = Query(default=50, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    if risk_level:
        query = query.filter(Alert.risk_level == risk_level)
    if resolved is not None:
        query = query.filter(Alert.is_resolved == resolved)
    return query.order_by(desc(Alert.created_at)).limit(limit).all()


@router.get("/summary")
def get_alerts_summary(db: Session = Depends(get_db)):
    """Overview counts for dashboard cards."""
    total    = db.query(Alert).count()
    active   = db.query(Alert).filter(Alert.is_resolved == False).count()
    critical = db.query(Alert).filter(
        Alert.risk_level == "critical", Alert.is_resolved == False
    ).count()
    warning  = db.query(Alert).filter(
        Alert.risk_level == "warning", Alert.is_resolved == False
    ).count()

    by_part = (
        db.query(Alert.pump_part, func.count())
        .filter(Alert.is_resolved == False)
        .group_by(Alert.pump_part)
        .all()
    )

    return {
        "total":           total,
        "active":          active,
        "critical":        critical,
        "warning":         warning,
        "active_by_part":  {part: count for part, count in by_part},
    }


@router.get("/{equipment_id}", response_model=List[AlertResponse])
def get_equipment_alerts(
    equipment_id: int,
    resolved: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(Alert).filter(Alert.equipment_id == equipment_id)
    if resolved is not None:
        query = query.filter(Alert.is_resolved == resolved)
    return query.order_by(desc(Alert.created_at)).all()


@router.get("/{equipment_id}/active", response_model=List[AlertResponse])
def get_active_alerts(equipment_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Alert)
        .filter(
            Alert.equipment_id == equipment_id,
            Alert.is_resolved  == False,
        )
        .order_by(desc(Alert.created_at))
        .all()
    )


@router.get("/{equipment_id}/by-part")
def get_alerts_by_part(equipment_id: int, db: Session = Depends(get_db)):
    """
    Returns active alert status per pump part.
    Used by the 3D visualization to color each part.
    """
    parts = ["bearing", "seal", "motor", "impeller"]

    result = {}
    for part in parts:
        alert = (
            db.query(Alert)
            .filter(
                Alert.equipment_id == equipment_id,
                Alert.pump_part    == part,
                Alert.is_resolved  == False,
            )
            .order_by(desc(Alert.created_at))
            .first()
        )
        result[part] = {
            "status":  alert.risk_level if alert else "normal",
            "message": alert.message    if alert else "Operating normally",
            "alert_id": alert.id        if alert else None,
        }

    return {
        "equipment_id": equipment_id,
        "parts":        result,
    }


@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_resolved = True
    db.commit()

    # Recalculate equipment status after resolve
    remaining = (
        db.query(Alert)
        .filter(
            Alert.equipment_id == alert.equipment_id,
            Alert.is_resolved  == False,
        )
        .all()
    )
    equipment = (
        db.query(Equipment)
        .filter(Equipment.id == alert.equipment_id)
        .first()
    )
    if equipment:
        equipment.status = get_equipment_status(
            [a.risk_level for a in remaining]
        )
        db.commit()

    return {
        "message":          f"Alert {alert_id} resolved",
        "equipment_status": equipment.status if equipment else "unknown",
    }