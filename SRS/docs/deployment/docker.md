# Docker

## Goals

- reproducible local setup
- consistent deployment packaging
- isolated service dependencies

## Proposed Services

- `web`
- `db`
- `redis`
- `worker`

## Example Compose Topology

```mermaid
flowchart LR
    B[Browser] --> W[web]
    W --> P[db]
    W --> R[redis]
    Q[worker] --> R
    Q --> P
```

