# Taller 3: API Mesa de Servicios para Laboratorios

## 1. Información General
* **Proyecto:** Sistema de gestión de tickets de servicios en laboratorios universitarios.
* **Asignatura:** Aplicaciones y Servicios Web
* **Fecha:** 2 de Mayo de 2026
* **Integrantes del Equipo:**
  * Diego Alejandro Giraldo Bolivar
  * Julian David Velez Arango
  * Jorge Andres Vidal Ramirez

## 2. Descripción del Sistema
API RESTful desarrollada con FastAPI para gestionar el ciclo de vida de los tickets de soporte técnico en los laboratorios de la universidad. El sistema implementa autenticación mediante JWT y autorización basada en *scopes* para controlar el acceso según cinco roles distintos (solicitante, responsable_tecnico, auxiliar, tecnico_especializado, admin). 

Se controlan estrictamente las transiciones de estado de los tickets y se valida la propiedad de los mismos para garantizar que solo el personal autorizado pueda atender o finalizar una solicitud.

**Entidades Implementadas:**
* **Usuarios:** Gestión de credenciales, roles y estado de actividad.
* **Laboratorios:** Catálogo de espacios físicos.
* **Servicios:** Tipos de soporte técnico ofrecidos.
* **Tickets:** Eje central del sistema que relaciona usuarios, laboratorios y servicios bajo un flujo de estados controlado.

## 3. Configuración del Entorno

Sigue estos pasos para ejecutar el proyecto localmente:

1. **Clonar el repositorio:**
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd taller3_fastapi

