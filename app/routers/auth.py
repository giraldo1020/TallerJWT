from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Importamos la conexión a la BD y los modelos
from db import get_db
from app.models.models import Usuario # Asumiendo que guardaste los modelos en app/models.py

# Importamos la lógica de seguridad
from app.security.security import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ROLES_SCOPES
)

# Definimos el router. 
# El prefix "/api/auth" coincide con el tokenUrl="api/auth/token" que pusimos en security.py
router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticación"]
)

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 1. Buscar al usuario en la BD (Usamos username del formulario para buscar el correo)
    usuario = db.query(Usuario).filter(Usuario.correo == form_data.username).first()
    
    # 2. Validar que el usuario exista
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Validar que la contraseña coincida con el hash
    if not verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 4. Validar que el usuario esté activo
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario está inactivo en el sistema"
        )

    # 5. Extraer los scopes permitidos según su rol (Definidos en security.py)
    scopes_permitidos = ROLES_SCOPES.get(usuario.rol, [])

    # 6. Preparar los datos del token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": usuario.correo,
            "id_usuario": usuario.id_usuario,
            "rol": usuario.rol,
            "scopes": scopes_permitidos
        },
        expires_delta=access_token_expires
    )

    # 7. Retornar el token en el formato exacto que exige OAuth2
    return {"access_token": access_token, "token_type": "bearer"}