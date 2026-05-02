from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ==========================================
# ESQUEMAS DE LABORATORIO
# ==========================================
class LaboratorioBase(BaseModel):
    nombre: str
    ubicacion: str
    activo: bool = True

class LaboratorioCreate(LaboratorioBase):
    pass

class LaboratorioResponse(LaboratorioBase):
    id_laboratorio: int

    class Config:
        from_attributes = True

# ==========================================
# ESQUEMAS DE SERVICIO
# ==========================================
class ServicioBase(BaseModel):
    nombre: str
    descripcion: str
    activo: bool = True

class ServicioCreate(ServicioBase):
    pass

class ServicioResponse(ServicioBase):
    id_servicio: int

    class Config:
        from_attributes = True