from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importamos la conexión a BD y el modelo
from db import get_db
from app.models.models import Laboratorio

# Importamos los esquemas (ajusta la ruta si los tienes en otro archivo como schemas.py)
from app.schemas.schemas import LaboratorioCreate, LaboratorioResponse

# Importamos la seguridad
from app.security.security import get_current_user

# ¡ESTA ES LA LÍNEA CRÍTICA QUE FASTAPI NO ENCONTRABA!
router = APIRouter(prefix="/api/laboratorios", tags=["Laboratorios"])

@router.post("/", response_model=LaboratorioResponse, status_code=status.HTTP_201_CREATED)
def crear_laboratorio(
    lab: LaboratorioCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["rol"] != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden crear laboratorios")
    
    nuevo_lab = Laboratorio(**lab.dict())
    db.add(nuevo_lab)
    db.commit()
    db.refresh(nuevo_lab)
    return nuevo_lab

@router.get("/", response_model=List[LaboratorioResponse])
def listar_laboratorios(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(Laboratorio).all()