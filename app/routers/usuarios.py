from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importamos la BD y los Modelos
from db import get_db
from app.models import Usuario

# Importamos los Schemas (asegúrate de que la ruta coincida con donde pusiste los esquemas)
from app.schemas import UsuarioCreate, UsuarioResponse

# Importamos la lógica de seguridad
from app.security.security import get_password_hash, get_current_user

router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuarios"]
)

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Verificar si el correo ya está registrado
    db_usuario = db.query(Usuario).filter(Usuario.correo == usuario.correo).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="El correo ya está registrado en el sistema")
    
    # 2. Crear la instancia del modelo SQLAlchemy (hasheando la contraseña)
    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        password_hash=get_password_hash(usuario.password),
        rol=usuario.rol,
        activo=usuario.activo
    )
    
    # 3. Guardar en la base de datos
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    # 4. FastAPI automáticamente lo convierte a UsuarioResponse (ocultando el password_hash)
    return nuevo_usuario

# Endpoint protegido: requiere scope "usuarios:gestionar" (solo admin)
@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    # Inyectamos el usuario actual, exigiendo el scope necesario
    current_user: dict = Depends(get_current_user) 
    # NOTA PARA EL EQUIPO: Para probar al inicio, pueden quitar el current_user temporalmente 
    # o asegurarse de crear un usuario con rol "admin" para listar.
):
    if "usuarios:gestionar" not in current_user["scopes"]:
         raise HTTPException(status_code=403, detail="No tienes permisos para listar usuarios")
         
    usuarios = db.query(Usuario).all()
    return usuarios