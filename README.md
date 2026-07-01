# Sistema de Mascotas Perdidas

Proyecto universitario que simula un sistema para reportar mascotas perdidas, buscar mascotas por foto y conectar con cuidadores.

## ¿Qué hace el proyecto?

Son 3 funcionalidades:

1. **Reporte de mascotas perdidas y alertas**: el dueño reporta su mascota como perdida (con foto obligatoria) y el sistema avisa automáticamente a personas cercanas dentro de un radio. Cualquier ciudadano (sin necesidad de cuenta) puede reportar que vio a la mascota.
2. **Buscador por imagen**: subes una foto y eliges qué quieres hacer con ella (verla en adopción, en venta, o ver si coincide con algún reporte de pérdida activo).
3. **Red de cuidadores**: gente que se registra para cuidar mascotas, con distintos roles y un sistema de calificaciones.

## Cómo está armado

Es un monorepo con dos carpetas principales:

```
apps/
├── api/   → Backend (FastAPI + PostgreSQL)
└── web/   → Frontend (React + Vite)
```

El backend está separado por dominios (`apps/api/app/domains/`): `users`, `pets`, `reports`, `sightings`, `notifications`, `caregivers`, `search`, `catalog`. Cada dominio tiene la misma estructura: `models.py` (tablas), `schemas.py` (validación), `repositories/` (acceso a datos), `services.py` (lógica), `routers.py` (endpoints).

Los patrones de diseño que usamos (Strategy, Repository, inyección de dependencias, principios SOLID) están explicados con más detalle en **`PATRONES_DISENO.md`**.

## Tecnologías usadas

**Backend**: FastAPI, SQLAlchemy (async), PostgreSQL, JWT para login, Alembic para migraciones, Pillow + imagehash para comparar fotos.

**Frontend**: React + TypeScript, Vite, Tailwind, Leaflet para el mapa.

## Cómo correrlo

Necesitas: Python 3.12 (si no tienes 3.11), Node.js, pnpm y Docker.

```bash
# 1. Levantar la base de datos (Postgres y Redis)
docker-compose up -d postgres redis

# 2. Backend
cd apps/api
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cp .env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --reload

# 3. Frontend (en otra terminal)
cd apps/web
pnpm install
cp .env.example .env.local
pnpm dev
```

- Backend: http://localhost:8000 (documentación de la API en `/docs`)
- Frontend: http://localhost:5173

### Convertir un usuario en administrador

Aprobar el documento de identidad de un cuidador requiere un usuario con rol `ADMIN`, pero no hay forma de registrarse como admin desde la app (para que nadie se auto-asigne el rol). Hay que registrarse normal y después correr esto en la base de datos:

```sql
UPDATE users SET role = 'ADMIN' WHERE email = 'tu_correo@ejemplo.com';
```

## Qué se implementó de los requerimientos

**Reporte y alertas**: registrar mascota con foto obligatoria, marcar ubicación con GPS o en un mapa (Leaflet), reportar avistamientos de forma anónima, y las alertas se mandan en segundo plano para no demorar la respuesta al usuario.

**Búsqueda por imagen**: las tres intenciones (adopción, venta, verificar pérdida) funcionan con un motor de comparación de fotos real (hashing perceptual, no resultados inventados). Venta solo muestra criaderos certificados. El catálogo de adopción/venta tiene datos de ejemplo cargados por migración, sin fotos reales todavía.

**Red de cuidadores**: los 3 roles, restricciones de servicio, calificaciones verificadas (solo puede calificar el dueño del reporte real), y el perfil de un cuidador queda oculto hasta que un admin aprueba su documento de identidad.

## Notas / cosas pendientes

- El catálogo de adopción/venta no tiene fotos reales, así que esos resultados no se comparan de verdad contra la imagen (solo se muestran con un puntaje fijo).
- No hay integración real con servicios externos (SMS, email push, S3) — están los puntos de extensión listos pero usan una implementación de consola/mock.
- `docker-compose.yml` solo levanta Postgres y Redis; el backend se corre aparte con `uvicorn`.

