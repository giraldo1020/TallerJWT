from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
# Importamos Base desde db.py que está en la raíz de tu proyecto
from db import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    # ESTO ES LO QUE OBLIGA A USAR TU SCHEMA
    __table_args__ = {"schema": "jwt_grupo_3"}

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    correo = Column(String, unique=True, index=True)
    password_hash = Column(String)
    rol = Column(String) 
    activo = Column(Boolean, default=True)

class Laboratorio(Base):
    __tablename__ = "laboratorios"
    __table_args__ = {"schema": "jwt_grupo_3"}

    id_laboratorio = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    ubicacion = Column(String)
    activo = Column(Boolean, default=True)

class Servicio(Base):
    __tablename__ = "servicios"
    __table_args__ = {"schema": "jwt_grupo_3"}

    id_servicio = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    descripcion = Column(String)
    activo = Column(Boolean, default=True)

class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = {"schema": "jwt_grupo_3"}

    id_ticket = Column(Integer, primary_key=True, index=True)
    # Fíjate que las Foreign Keys también deben incluir el schema para que no fallen
    id_solicitante = Column(Integer, ForeignKey("jwt_grupo_3.usuarios.id_usuario"))
    id_laboratorio = Column(Integer, ForeignKey("jwt_grupo_3.laboratorios.id_laboratorio"))
    id_servicio = Column(Integer, ForeignKey("jwt_grupo_3.servicios.id_servicio"))
    id_responsable = Column(Integer, ForeignKey("jwt_grupo_3.usuarios.id_usuario"), nullable=True)
    id_asignado = Column(Integer, ForeignKey("jwt_grupo_3.usuarios.id_usuario"), nullable=True)
    
    titulo = Column(String, index=True)
    descripcion = Column(String)
    estado = Column(String, default="solicitado") 
    prioridad = Column(String)
    observacion_responsable = Column(String, nullable=True)
    observacion_tecnico = Column(String, nullable=True)
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_finalizacion = Column(DateTime, nullable=True)

    # Relaciones para facilitar consultas con el ORM
    solicitante = relationship("Usuario", foreign_keys=[id_solicitante])
    responsable = relationship("Usuario", foreign_keys=[id_responsable])
    asignado = relationship("Usuario", foreign_keys=[id_asignado])