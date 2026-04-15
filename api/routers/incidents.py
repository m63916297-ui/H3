from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid
import h3

from db.database import get_db
from db.models import Incident, User
from core.h3_utils import get_h3_index as get_h3_index_util, get_h3_center
from core.security import get_password_hash, verify_password, create_access_token
from api.models.schemas import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    UserCreate,
    UserLogin,
    Token,
    ApiResponse,
    H3DensityResponse,
    HealthResponse,
)
from core.config import settings


router = APIRouter(prefix="/api/v1", tags=["incidents"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok", version="1.0.0", timestamp=datetime.utcnow().isoformat()
    )


@router.post(
    "/incidents", response_model=ApiResponse, status_code=status.HTTP_201_CREATED
)
def create_incident(incident_data: IncidentCreate, db: Session = Depends(get_db)):
    incident_id = str(uuid.uuid4())

    h3_index = get_h3_index_util(
        incident_data.location.latitude, incident_data.location.longitude
    )
    center_lat, center_lng = get_h3_center(h3_index)

    db_incident = Incident(
        id=incident_id,
        title=incident_data.title,
        description=incident_data.description,
        category=incident_data.category,
        tipo_reporte=incident_data.tipo_reporte,
        ley=incident_data.ley,
        severity=incident_data.severity,
        fuente=incident_data.fuente,
        latitude=incident_data.location.latitude,
        longitude=incident_data.location.longitude,
        address=incident_data.location.address,
        h3_index=h3_index,
        h3_center_lat=center_lat,
        h3_center_lng=center_lng,
        resolution=settings.H3_RESOLUTION,
        reporter_name=incident_data.reporter_name,
        reporter_contact=incident_data.reporter_contact,
        reporter_type=incident_data.reporter_type,
        es_anonimo=incident_data.es_anonimo,
        status="recibido",
        timestamp=datetime.utcnow(),
    )

    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    return ApiResponse(status="ok", data=db_incident.to_dict(), meta={"total": 1})


@router.get("/incidents", response_model=ApiResponse)
def list_incidents(
    category: Optional[str] = Query(None),
    tipo_reporte: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    h3_index: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(Incident)

    if category:
        query = query.filter(Incident.category == category)
    if tipo_reporte:
        query = query.filter(Incident.tipo_reporte == tipo_reporte)
    if status:
        query = query.filter(Incident.status == status)
    if h3_index:
        query = query.filter(Incident.h3_index == h3_index)
    if start_date:
        query = query.filter(Incident.timestamp >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Incident.timestamp <= datetime.fromisoformat(end_date))

    total = query.count()
    incidents = query.offset(skip).limit(limit).all()

    return ApiResponse(
        status="ok",
        data={"incidents": [i.to_dict() for i in incidents]},
        meta={"total": total, "skip": skip, "limit": limit},
    )


@router.get("/incidents/{incident_id}", response_model=ApiResponse)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        )

    return ApiResponse(status="ok", data=incident.to_dict(), meta={"total": 1})


@router.put("/incidents/{incident_id}", response_model=ApiResponse)
def update_incident(
    incident_id: str, incident_data: IncidentUpdate, db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        )

    update_data = incident_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(incident, field, value)

    incident.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)

    return ApiResponse(status="ok", data=incident.to_dict(), meta={"total": 1})


@router.delete("/incidents/{incident_id}", response_model=ApiResponse)
def delete_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        )

    incident.status = "cerrado"
    db.commit()

    return ApiResponse(
        status="ok", data={"message": "Incident deleted"}, meta={"id": incident_id}
    )


@router.get("/h3/{index}/density", response_model=ApiResponse)
def get_h3_density(
    index: str, k: int = Query(1, ge=1, le=5), db: Session = Depends(get_db)
):
    try:
        neighbors = h3.grid_disk(index, k)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid H3 index"
        )

    incidents = db.query(Incident).filter(Incident.h3_index.in_(neighbors)).all()

    density_data = []
    for h3_idx in neighbors:
        count = sum(1 for i in incidents if i.h3_index == h3_idx)
        if count > 0 or k == 1:
            center_lat, center_lng = h3.cell_to_latlng(h3_idx)
            density_data.append(
                H3DensityResponse(
                    h3_index=h3_idx,
                    count=count,
                    center_lat=center_lat,
                    center_lng=center_lng,
                )
            )

    return ApiResponse(
        status="ok",
        data={"density": [d.model_dump() for d in density_data]},
        meta={"total_cells": len(density_data), "k": k},
    )
