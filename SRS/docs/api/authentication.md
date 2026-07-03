# Authentication API

## Approach

The API should support either session authentication for server-rendered views or token/JWT authentication for SPA or mobile clients.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/auth/login/` | Sign in |
| `POST` | `/api/v1/auth/logout/` | Sign out |
| `POST` | `/api/v1/auth/register/` | Create account |
| `GET` | `/api/v1/auth/me/` | Current user profile |

## Notes

- Rate limit login attempts.
- Require CSRF protection for session-based flows.

