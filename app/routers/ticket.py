from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from sqlalchemy import or_

from db import get_db
from app.models.models import Ticket
from app.schemas.ticket import TicketCreate, TicketResponse, TicketEstadoUpdate
from app.security.security import get_current_user

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

# Reglas de la máquina de estados según la guía
TRANSICIONES_PERMITIDAS = {
    "solicitado": {"siguiente": "recibido", "scope_requerido": "tickets:recibir"},
    "recibido": {"siguiente": "asignado", "scope_requerido": "tickets:asignar"},
    "asignado": {"siguiente": "en_proceso", "scope_requerido": "tickets:atender"},
    "en_proceso": {"siguiente": "en_revision", "scope_requerido": "tickets:atender"},
    "en_revision": {"siguiente": "terminado", "scope_requerido": "tickets:finalizar"},
}

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def crear_ticket(
    ticket: TicketCreate, 
    db: Session = Depends(get_db),
    # Exigimos el scope 'tickets:crear' (solicitantes y admins lo tienen)
    current_user: dict = Security(get_current_user, scopes=["tickets:crear"])
):
    # Inyectamos automáticamente el id del usuario autenticado como solicitante
    nuevo_ticket = Ticket(**ticket.dict(), id_solicitante=current_user["id_usuario"])
    db.add(nuevo_ticket)
    db.commit()
    db.refresh(nuevo_ticket)
    return nuevo_ticket

@router.get("/", response_model=List[TicketResponse])
def listar_tickets(
    db: Session = Depends(get_db),
    # Pedimos el scope base de lectura
    current_user: dict = Security(get_current_user, scopes=["tickets:ver_propios"])
):
    id_user = current_user["id_usuario"]
    rol = current_user["rol"]

    # Si es admin, lo ve todo (Scope: ver_todos)
    if rol == "admin":
        return db.query(Ticket).all()
    
    # Para los demás, aplicamos la regla de "Visibilidad":
    # Solo ven tickets donde son solicitantes, responsables o asignados.
    tickets = db.query(Ticket).filter(
        or_(
            Ticket.id_solicitante == id_user,
            Ticket.id_responsable == id_user,
            Ticket.id_asignado == id_user
        )
    ).all()
    
    # Extra: Si es responsable_tecnico, también debería poder ver los tickets 'solicitados' 
    # para poder recibirlos.
    if rol == "responsable_tecnico":
        tickets_nuevos = db.query(Ticket).filter(Ticket.estado == "solicitado").all()
        # Unimos las listas sin duplicados
        tickets = list({t.id_ticket: t for t in (tickets + tickets_nuevos)}.values())

    return tickets

@router.patch("/{id_ticket}/estado", response_model=TicketResponse)
def actualizar_estado_ticket(
    id_ticket: int, 
    update_data: TicketEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) # Evaluamos el scope dentro de la función
):
    ticket = db.query(Ticket).filter(Ticket.id_ticket == id_ticket).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    estado_actual = ticket.estado
    nuevo_estado = update_data.nuevo_estado

    # 1. Validar la transición permitida
    if estado_actual not in TRANSICIONES_PERMITIDAS or TRANSICIONES_PERMITIDAS[estado_actual]["siguiente"] != nuevo_estado:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=f"Transición no permitida. De '{estado_actual}' solo se puede pasar a '{TRANSICIONES_PERMITIDAS.get(estado_actual, {}).get('siguiente', 'ninguno')}'"
        )

    # 2. Validar el Scope del usuario para esta acción
    scope_necesario = TRANSICIONES_PERMITIDAS[estado_actual]["scope_requerido"]
    if scope_necesario not in current_user["scopes"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"No tienes el permiso ({scope_necesario}) para hacer este cambio."
        )

    # 3. Validar Reglas de Negocio y Propiedad
    id_user = current_user["id_usuario"]
    rol = current_user["rol"]

    if nuevo_estado == "recibido":
        # Quien lo recibe se convierte en el responsable
        ticket.id_responsable = id_user
    
    elif nuevo_estado == "asignado":
        # Se debe proveer a quién se le asigna
        if not update_data.id_asignado:
            raise HTTPException(status_code=422, detail="Para asignar un ticket, debes enviar el id_asignado")
        ticket.id_asignado = update_data.id_asignado
        if update_data.observacion:
            ticket.observacion_responsable = update_data.observacion

    elif nuevo_estado in ["en_proceso", "en_revision"]:
        # Solo el asignado (o admin) puede atenderlo
        if rol != "admin" and ticket.id_asignado != id_user:
            raise HTTPException(status_code=403, detail="No puedes atender un ticket que no te fue asignado")
        if update_data.observacion:
            ticket.observacion_tecnico = update_data.observacion

    elif nuevo_estado == "terminado":
        # Solo el responsable original (o admin) puede cerrarlo
        if rol != "admin" and ticket.id_responsable != id_user:
            raise HTTPException(status_code=403, detail="Solo el responsable técnico que recibió el ticket puede finalizarlo")
        ticket.fecha_finalizacion = datetime.utcnow()

    # 4. Guardar cambios
    ticket.estado = nuevo_estado
    db.commit()
    db.refresh(ticket)
    return ticket