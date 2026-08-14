# Smart Agriculture & Farm Management System

A REST API built with **FastAPI** for managing farms, fields, crops, irrigation, fertilizer/pesticide
treatments, crop health, harvests, and produce sales — with JWT authentication, role-based access
control, search/filtering/pagination, and dashboard reporting.

## Tech Stack

- Python 3.10+
- FastAPI + Pydantic v2
- SQLAlchemy ORM (SQLite by default, PostgreSQL-ready)
- JWT authentication (PyJWT) with `pbkdf2_sha256` password hashing (passlib)
- Uvicorn ASGI server
- Pytest for automated tests

## Project Structure

```
app/
├── main.py              # App wiring, middleware, global exception handlers
├── database.py           # SQLAlchemy engine/session/Base
├── config.py              # Environment-based settings (pydantic-settings)
├── models/                # SQLAlchemy ORM models + enums
├── schemas/                # Pydantic request/response schemas
├── routes/                  # FastAPI routers (one file per resource)
├── services/                 # Business logic / DB access, kept out of routes
├── utils/                     # security (JWT/hashing), auth deps, pagination
└── tests/                      # Pytest test suite (in-memory SQLite)
requirements.txt
.env.example
```

This mirrors the requested clean-architecture layout, with routes calling services, and services
owning all business rules and database queries.

## Getting Started

```bash
# 1. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment (optional — sensible defaults are built in)
cp .env.example .env
# edit .env to set a real SECRET_KEY and, if desired, a PostgreSQL DATABASE_URL

# 4. Run the server
uvicorn app.main:app --reload

# App:    http://127.0.0.1:8000
# Docs:   http://127.0.0.1:8000/docs   (Swagger UI)
# Redoc:  http://127.0.0.1:8000/redoc
```

Tables are created automatically on startup via `Base.metadata.create_all()` — no migration step
needed for local development. Swap in Alembic for production schema migrations.

### Running tests

```bash
pytest -v
```

The suite spins up an isolated in-memory SQLite database per test and covers registration/login,
role enforcement, farm/field area validation, crop overlap rules, and a full crop → irrigation →
treatment → health → harvest → sale workflow (12 tests, all passing).

## Roles & Permissions

| Role           | Farms/Fields | Crops | Irrigation / Treatments / Health | Harvest / Sales | Dashboard |
|----------------|:---:|:---:|:---:|:---:|:---:|
| Admin          | ✅ full | ✅ full | ✅ full | ✅ full | ✅ |
| Farm Manager   | ✅ full | ✅ full | ✅ full | ✅ full | ✅ |
| Farmer         | 👁 read only | ✅ create/update | ✅ record | ✅ full | ❌ |
| Field Worker   | 👁 read only | 👁 read only | ✅ record | ❌ | ❌ |

All authenticated users can **read/list** farms, fields, and crops. Everyone must hold a valid
JWT (`Authorization: Bearer <token>`) except `POST /auth/register` and `POST /auth/login`.

> **Assumption:** `/auth/register` currently accepts a `role` field for any role, including
> `admin`, to keep the assignment self-contained (there'd otherwise be no way to create the very
> first admin). In a production system, admin/manager creation should be restricted to existing
> admins.

## API Overview

### Auth
- `POST /auth/register` — create a user (`full_name`, `email`, `password`, `role`)
- `POST /auth/login` — returns a JWT bearer token + user profile
- `GET /auth/me` — current authenticated user

### Farms & Fields
- `POST /farms`, `GET /farms` (search by `location`, filter by `status`, paginated/sortable)
- `GET /farms/{farm_id}`, `PUT /farms/{farm_id}`
- `POST /farms/{farm_id}/fields`, `GET /farms/{farm_id}/fields`

### Crops
- `POST /crops`, `GET /crops` (search by `crop_name`, filter by `status`/date range)
- `GET /crops/{crop_id}`, `PUT /crops/{crop_id}`

### Irrigation
- `POST /irrigation`, `GET /irrigation`, `GET /fields/{field_id}/irrigation`

### Fertilizer & Pesticide Treatments
- `POST /crop-treatments`, `GET /crop-treatments`, `GET /crops/{crop_id}/treatments`

### Crop Health
- `POST /crop-health`, `GET /crop-health`, `GET /crops/{crop_id}/health-history`

### Harvest
- `POST /harvests`, `GET /harvests` (filter by `quality_grade`/`harvest_date`)
- `GET /crops/{crop_id}/harvest`

### Sales
- `POST /sales`, `GET /sales` (filter by `payment_status`/`buyer_name`), `GET /sales/{sale_id}`

### Dashboard & Reports
- `GET /dashboard/summary` — totals: farms, fields, active crops, crops ready for harvest,
  critical alerts, harvested quantity, sales count, revenue, treatment cost
- `GET /dashboard/reports` — farm-wise revenue + crop-wise production

All list endpoints accept `page`, `limit`, `sort_by`, `sort_order` query params and return:
```json
{ "total": 0, "page": 1, "limit": 10, "total_pages": 0, "items": [] }
```

## Business Rules Implemented

- Field area cannot exceed the farm's *available* (unallocated) area.
- Inactive fields cannot be used for new crop cultivation.
- A field cannot have two overlapping active crop cycles (Planned/Growing/Ready for Harvest).
- Planting date cannot be after the (expected) harvest date — enforced on both create and update.
- Harvested crops cannot be modified.
- Irrigation can only be recorded for a field that currently has an active crop.
- Fertilizer/pesticide quantity and cost must be greater than 0.
- A **Critical** crop health inspection automatically raises an alert (visible via
  `dashboard/summary.critical_crop_alerts`), conceptually routed to the Farm Manager.
- Harvest can only be created when a crop's status is `Ready for Harvest`; doing so automatically
  flips the crop to `Harvested`.
- Sales cannot exceed the harvested quantity still remaining for that harvest record.
- `total_amount` on a sale is always server-computed (`quantity × price_per_unit`), never trusted
  from the client.

## Error Handling

A global exception handler layer returns a consistent JSON envelope for every error:

```json
{ "success": false, "message": "Field area (20) exceeds the farm's available area (10)", "data": null }
```

Pydantic validation failures return `422` with a structured `errors` array; any unhandled
exception is caught and logged, returning a generic `500` without leaking internals.

## Example: Register → Login → Create a Farm

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Admin User","email":"admin@example.com","password":"password123","role":"admin"}'

curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password123"}'
# => { "access_token": "...", "token_type": "bearer", "user": { ... } }

curl -X POST http://127.0.0.1:8000/farms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"farm_name":"Green Acres","location":"Chennai","total_area":100,"owner_name":"Farmer John"}'
```

## Notes / Design Decisions

- Passwords are hashed with `pbkdf2_sha256` (no native/compiled dependency required, unlike
  bcrypt), and JWTs are signed with HS256 using `SECRET_KEY` from the environment.
- SQLite is the default database for zero-setup local development; set `DATABASE_URL` in `.env`
  to point at PostgreSQL (e.g. `postgresql://user:pass@localhost:5432/agri_db`) for production.
- `unit`, `soil_type`, `irrigation_type`, and `quality_grade` are free-text strings rather than
  closed enums, since the assignment doesn't fix a controlled vocabulary for them.
