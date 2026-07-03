# Applications API

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/applications/` | List applications |
| `POST` | `/api/v1/applications/` | Create application |
| `GET` | `/api/v1/applications/{id}/` | Retrieve application |
| `PATCH` | `/api/v1/applications/{id}/` | Update application |
| `DELETE` | `/api/v1/applications/{id}/` | Delete application |

## Example Payload

```json
{
  "company_id": "uuid",
  "title": "Backend Engineer",
  "source": "LinkedIn",
  "status": "applied",
  "applied_at": "2026-07-01",
  "notes": "Submitted with referral"
}
```

