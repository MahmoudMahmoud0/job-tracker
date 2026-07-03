# Acceptance Criteria

## Create Application

- Given an authenticated user
- When they submit a valid application form
- Then the system creates the application under their account
- And the application appears in the default list view

## Update Status

- Given an existing application owned by the user
- When the user changes the status
- Then the new status is saved
- And a status history entry is recorded with timestamp and actor

## Schedule Interview

- Given an application in an active pipeline stage
- When the user creates an interview with a future date
- Then the interview is linked to that application
- And it appears in upcoming events views

## View Dashboard

- Given a user with existing data
- When they open the dashboard
- Then they see counts by status, recent activity, and upcoming interviews

