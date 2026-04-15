from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20))
    role = Column(String(20), default="ciudadano")
    created_at = Column(DateTime, default=datetime.utcnow)

    incidents = relationship("Incident", back_populates="reporter")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False, index=True)
    tipo_reporte = Column(String(20), nullable=False)
    ley = Column(String(20))
    severity = Column(Integer, default=1)
    fuente = Column(String(50), default="ciudadano")

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(255))
    h3_index = Column(String(15), index=True)
    h3_center_lat = Column(Float)
    h3_center_lng = Column(Float)
    resolution = Column(Integer, default=8)

    reporter_name = Column(String(100))
    reporter_contact = Column(String(100))
    reporter_type = Column(String(20), default="Anonimo")
    es_anonimo = Column(Boolean, default=False)

    status = Column(String(20), default="recibido", index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reporter = relationship("User", back_populates="incidents")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "tipo_reporte": self.tipo_reporte,
            "ley": self.ley,
            "severity": self.severity,
            "fuente": self.fuente,
            "location": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "address": self.address,
            },
            "h3_index": self.h3_index,
            "h3_center_lat": self.h3_center_lat,
            "h3_center_lng": self.h3_center_lng,
            "resolution": self.resolution,
            "reporter_name": self.reporter_name,
            "reporter_contact": self.reporter_contact,
            "reporter_type": self.reporter_type,
            "es_anonimo": self.es_anonimo,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
