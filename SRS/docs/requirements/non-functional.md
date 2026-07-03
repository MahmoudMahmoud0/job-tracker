# Non-Functional Requirements

## Performance

- Typical dashboard views should load in under 2 seconds for a user with up to 5,000 application records.
- List filtering actions should return results in under 1 second under expected load.

## Security

- All authenticated endpoints must require secure session or token validation.
- Sensitive data must be encrypted in transit using HTTPS.
- Passwords must be hashed using a strong one-way algorithm supported by Django.

## Reliability

- The production environment should target 99.5% monthly availability.
- Backups must run daily and support point-in-time recovery where feasible.

## Maintainability

- Backend code should be organized by bounded apps with clear model ownership.
- API contracts should be versioned to reduce breaking changes.
- Test coverage should focus on business rules, permissions, and state transitions.

## Usability

- New users should be able to record their first application in less than 5 minutes from sign-up.
- Primary workflows must remain usable on mobile viewport sizes.

