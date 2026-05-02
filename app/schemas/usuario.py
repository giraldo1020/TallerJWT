from pydantic import BaseModel, EmailStr
from typing import Optional

# 1. Esquema Base: Propiedades compartidas
class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr  # EmailStr valida automáticamente que tenga formato de correo
    rol: str
    activo: bool = True

# 2. Esquema de Creación: Lo que pedimos cuando un usuario se registra
# Hereda de UsuarioBase y añade la contraseña (en texto plano, que luego hashearemos)
class UsuarioCreate(UsuarioBase):
    password: str

# 3. Esquema de Respuesta: Lo que devolvemos al cliente
# NUNCA devolvemos la contraseña. Añadimos el ID generado por la BD.
class UsuarioResponse(UsuarioBase):
    id_usuario: int

    class Config:
        # Esto es crucial para que Pydantic sepa leer los objetos de SQLAlchemy
        from_attributes = True