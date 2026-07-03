# Companies API

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/companies/` | List companies |
| `POST` | `/api/v1/companies/` | Create company |
| `GET` | `/api/v1/companies/{id}/` | Retrieve company |
| `PATCH` | `/api/v1/companies/{id}/` | Update company |
| `DELETE` | `/api/v1/companies/{id}/` | Delete company |

## Validation

- `name` is required
- `website` must be a valid URL when provided
- ownership is enforced server-side

