# Interviews API

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/interviews/` | List interviews |
| `POST` | `/api/v1/interviews/` | Create interview |
| `GET` | `/api/v1/interviews/{id}/` | Retrieve interview |
| `PATCH` | `/api/v1/interviews/{id}/` | Update interview |
| `DELETE` | `/api/v1/interviews/{id}/` | Delete interview |

## Business Rules

- interviews must reference an application owned by the caller
- `scheduled_at` must be timezone-aware and valid

