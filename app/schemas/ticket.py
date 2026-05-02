from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ==========================================
# ESQUEMAS DE TICKET
# ==========================================
class TicketBase(BaseModel):
    id_laboratorio: int
    id_servicio: int
    titulo: str
    descripcion: str
    prioridad: str  # Nota: idealmente esto sería un Enum (baja, media, alta), pero dejémoslo en string por simplicidad del taller.

class TicketCreate(TicketBase):
    # Hereda titulo, descripcion, etc. 
    # NO incluimos id_solicitante, id_responsable, ni estado aquí.
    pass

class TicketEstadoUpdate(BaseModel):
    # Este esquema es exclusivo para el PATCH /tickets/{id}/estado
    nuevo_estado: str
    observacion: Optional[str] = None # Opcional: por si el técnico o responsable quiere dejar un comentario al cambiar el estado
    id_asignado: Optional[int] = None

class TicketResponse(TicketBase):
    id_ticket: int
    id_solicitante: int
    id_responsable: Optional[int] = None
    id_asignado: Optional[int] = None
    estado: str
    observacion_responsable: Optional[str] = None
    observacion_tecnico: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    fecha_finalizacion: Optional[datetime] = None

    class Config:
        from_attributes = True