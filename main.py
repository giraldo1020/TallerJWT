from fastapi import FastAPI
from db import engine, Base

# Importamos los routers
from app.routers import auth, usuarios

# IMPORTANTE: Esto le dice a SQLAlchemy que cree las tablas en la base de datos 
# si no existen. Ojo: El esquema 'jwt_grupo_3' ya debe haber sido creado por 
# el profesor o por ustedes directamente en PostgreSQL mediante un comando SQL 
# como: CREATE SCHEMA jwt_grupo_3;
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Taller 3 - Mesa de Servicios",
    description="Implementación de JWT y Scopes para la asignatura Aplicaciones y Servicios Web.",
    version="1.0.0"
)

# Registramos los routers en la aplicación
app.include_router(auth.router)
app.include_router(usuarios.router)

@app.get("/")
def read_root():
    return {"mensaje": "API Mesa de Servicios Activa. Visita /docs para probar los endpoints."}