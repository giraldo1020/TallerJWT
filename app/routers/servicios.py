from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db import get_db
from app.models import Servicio
from app.schemas import ServicioCreate, ServicioResponse
from app.security.security import get_current_user

router = APIRouter(prefix="/api/servicios", tags=["Servicios"])

@router.post("/", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
def crear_servicio(
    servicio: ServicioCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["rol"] != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden crear servicios")
    
    nuevo_servicio = Servicio(**servicio.dict())
    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)
    return nuevo_servicio

@router.get("/", response_model=List[ServicioResponse])
def listar_servicios(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(Servicio).all()