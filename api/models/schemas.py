from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class LocationSchema(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None


class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = Field(..., pattern="^(hurto|violencia|convivencia)$")
    tipo_reporte: str = Field(..., pattern="^(rapido|convivencia|delito)$")
    ley: Optional[str] = Field(None, pattern="^(1801/2016|599/2000)$")
    severity: int = Field(default=1, ge=1, le=5)
    fuente: str = Field(default="ciudadano")
    location: LocationSchema
    reporter_name: Optional[str] = None
    reporter_contact: Optional[str] = None
    reporter_type: str = Field(default="Anonimo")
    es_anonimo: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Hurto en la calle principal",
                "description": "Me robaron el celular en el bus",
                "category": "hurto",
                "tipo_reporte": "delito",
                "ley": "599/2000",
                "severity": 3,
                "fuente": "ciudadano",
                "location": {
                    "latitude": 4.7110,
                    "longitude": -74.0721,
                    "address": "Calle 10 # 5-21, Centro",
                },
                "reporter_name": "Juan Perez",
                "reporter_contact": "juan@email.com",
                "reporter_type": "Email",
                "es_anonimo": False,
            }
        }


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = Field(
        None, pattern="^(recibido|en_proceso|resuelto|cerrado)$"
    )
    severity: Optional[int] = Field(None, ge=1, le=5)


class IncidentResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: str
    tipo_reporte: str
    ley: Optional[str] = None
    severity: int
    fuente: str
    location: LocationSchema
    h3_index: Optional[str] = None
    h3_center_lat: Optional[float] = None
    h3_center_lng: Optional[float] = None
    resolution: Optional[int] = None
    reporter_name: Optional[str] = None
    reporter_contact: Optional[str] = None
    reporter_type: Optional[str] = None
    es_anonimo: bool
    status: str
    timestamp: str
    created_at: str
    updated_at: str


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: str = Field(default="ciudadano")


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class H3DensityResponse(BaseModel):
    h3_index: str
    count: int
    center_lat: float
    center_lng: float


class ApiResponse(BaseModel):
    status: str
    data: Optional[dict] = None
    meta: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    timestamp: str
