from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import httpx
from typing import Optional

from db.database import get_db
from db.models import Incident
from api.models.schemas import ApiResponse
from core.config import settings
from core.security import verify_api_key


router = APIRouter(prefix="/api/v1/external", tags=["external"])


@router.post("/sync", response_model=ApiResponse)
def trigger_external_sync(api_key: str, db: Session = Depends(get_db)):
    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key"
        )

    incidents = (
        db.query(Incident).filter(Incident.status == "recibido").limit(100).all()
    )

    payload = {"incidents": [i.to_dict() for i in incidents], "total": len(incidents)}

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                settings.EXTERNAL_API_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
    except httpx.RequestError as e:
        return ApiResponse(
            status="error", data={"message": str(e)}, meta={"synced_count": 0}
        )

    for incident in incidents:
        incident.status = "en_proceso"
        db.commit()

    return ApiResponse(
        status="ok",
        data={"synced_count": len(incidents)},
        meta={"total": len(incidents)},
    )


@router.get("/incidents/export", response_model=ApiResponse)
def export_incidents(api_key: str, format: str = "json", db: Session = Depends(get_db)):
    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key"
        )

    incidents = db.query(Incident).all()

    if format == "csv":
        import csv
        import io

        output = io.StringIO()
        if incidents:
            headers = [
                "id",
                "title",
                "category",
                "tipo_reporte",
                "severity",
                "status",
                "timestamp",
            ]
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            for i in incidents:
                writer.writerow(
                    {
                        "id": i.id,
                        "title": i.title,
                        "category": i.category,
                        "tipo_reporte": i.tipo_reporte,
                        "severity": i.severity,
                        "status": i.status,
                        "timestamp": i.timestamp.isoformat(),
                    }
                )
        return ApiResponse(
            status="ok",
            data={"csv": output.getvalue()},
            meta={"total": len(incidents), "format": "csv"},
        )

    return ApiResponse(
        status="ok",
        data={"incidents": [i.to_dict() for i in incidents]},
        meta={"total": len(incidents), "format": "json"},
    )
