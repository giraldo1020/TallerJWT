import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Configuraciones desde el .env
SECRET_KEY = os.getenv("SECRET_KEY", "clave_super_secreta_por_defecto")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Configuración de Hashes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Definición de la URL donde Swagger enviará las credenciales y los scopes documentados
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth/token",
    scopes={
        "tickets:crear": "Crear nuevos tickets",
        "tickets:ver_propios": "Ver tickets propios",
        "tickets:recibir": "Recibir tickets",
        "tickets:asignar": "Asignar tickets",
        "tickets:atender": "Atender tickets",
        "tickets:finalizar": "Finalizar tickets",
        "tickets:ver_todos": "Ver todos los tickets",
        "usuarios:gestionar": "Gestionar usuarios"
    }
)

# Diccionario de reglas según la guía del Taller
ROLES_SCOPES = {
    "solicitante": ["tickets:crear", "tickets:ver_propios"],
    "responsable_tecnico": ["tickets:ver_propios", "tickets:recibir", "tickets:asignar", "tickets:finalizar"],
    "auxiliar": ["tickets:ver_propios", "tickets:atender"],
    "tecnico_especializado": ["tickets:ver_propios", "tickets:atender"],
    "admin": ["tickets:crear", "tickets:ver_propios", "tickets:recibir", "tickets:asignar", "tickets:atender", "tickets:finalizar", "tickets:ver_todos", "usuarios:gestionar"]
}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Esta es la dependencia crítica que usaremos en las rutas protegidas
async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        # Decodificamos el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise credentials_exception
        
        # Extraemos la información que inyectamos al hacer login
        token_scopes = payload.get("scopes", [])
        id_usuario: int = payload.get("id_usuario")
        rol: str = payload.get("rol")
    except JWTError:
        raise credentials_exception

    # Magia de FastAPI: Verifica si el scope que pide el endpoint está dentro de los scopes del token
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permisos insuficientes. Requiere el scope: {scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    # Retornamos el diccionario del usuario actual para que el endpoint lo use (ej: validar propiedad del ticket)
    return {
        "correo": correo, 
        "id_usuario": id_usuario, 
        "rol": rol, 
        "scopes": token_scopes
    }