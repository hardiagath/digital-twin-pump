from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Equipment
from app.schemas.schemas import EquipmentResponse
from typing import List

router = APIRouter(prefix="/equipment", tags=["Equipment"])

@router.get("/", response_model=List[EquipmentResponse])
def get_all_equipment(db: Session = Depends(get_db)):
    return db.query(Equipment).all()

@router.get("/{equipment_id}", response_model=EquipmentResponse)
def get_equipment(equipment_id: int, db: Session = Depends(get_db)):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@router.get("/{equipment_id}/status")
def get_equipment_status(equipment_id: int, db: Session = Depends(get_db)):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return {
        "equipment_id": equipment_id,
        "name": equipment.name,
        "status": equipment.status,
        "location": equipment.location
    }