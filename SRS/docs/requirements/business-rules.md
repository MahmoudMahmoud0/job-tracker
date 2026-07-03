# Business Rules

## Application Rules

- An application belongs to exactly one user and one company.
- An application may exist without interviews, but an interview cannot exist without an application.
- Pipeline status changes must be timestamped.
- Closed statuses such as `rejected`, `withdrawn`, or `offer_accepted` should prevent further active reminders unless explicitly re-opened.

## Scheduling Rules

- Interview times must be stored in a timezone-aware format.
- Reminder offsets should be configurable per user.

## Data Integrity Rules

- Users cannot access or mutate records owned by another user.
- Duplicate applications to the same company and role are allowed, but the UI should warn before creating them.
- Company names are not globally unique and must not be used as the sole key.

