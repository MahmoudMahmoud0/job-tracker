# Permissions

## Permission Model

The default design is user-owned data with optional staff administration.

| Role | Applications | Companies | Interviews | Reports | Admin Views |
| --- | --- | --- | --- | --- | --- |
| User | CRUD own | CRUD own | CRUD own | View own | No |
| Staff | Read support scope | Read support scope | Read support scope | Limited aggregate | Yes |
| Admin | Full | Full | Full | Full | Yes |

## Enforcement Layers

- route-level authentication
- queryset scoping by owner
- object-level authorization checks
- serializer validation for foreign-key ownership

