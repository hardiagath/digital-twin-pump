from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.models import Recommendation, Alert
from app.schemas.schemas import RecommendationResponse
from app.services.recommendation_service import fetch_or_create_recommendation
from typing import List

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/alert/{alert_id}", response_model=RecommendationResponse)
def get_recommendation_for_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Fetch recommendation for a specific alert.
    Generates via Gemini if not already cached.
    """
    try:
        return fetch_or_create_recommendation(alert_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")


@router.get("/equipment/{equipment_id}", response_model=List[RecommendationResponse])
def get_recommendations_for_equipment(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    """Return all recommendations for an equipment's alerts."""
    return (
        db.query(Recommendation)
        .filter(Recommendation.equipment_id == equipment_id)
        .order_by(desc(Recommendation.generated_at))
        .all()
    )


@router.post("/generate-all")
def generate_all_recommendations(db: Session = Depends(get_db)):
    """
    Bulk generate recommendations for all unresolved alerts
    that don't have one yet. Useful for initial setup.
    """
    alerts = (
        db.query(Alert)
        .filter(Alert.is_resolved == False)
        .all()
    )

    generated = 0
    skipped   = 0
    failed    = 0

    for alert in alerts:
        existing = db.query(Recommendation).filter(
            Recommendation.alert_id == alert.id
        ).first()

        if existing:
            skipped += 1
            continue

        try:
            fetch_or_create_recommendation(alert.id, db)
            generated += 1
        except Exception:
            failed += 1

    return {
        "generated": generated,
        "skipped":   skipped,
        "failed":    failed,
        "total":     len(alerts),
    }