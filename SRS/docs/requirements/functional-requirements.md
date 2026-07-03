# Functional Requirements

## Core Modules

### Application Tracking

- The system shall allow a user to create an application with role title, company, source, status, date applied, and notes.
- The system shall allow a user to edit, archive, and delete their own applications.
- The system shall maintain a status history for each application.
- The system shall support filtering applications by status, company, date range, source, and tags.

### Company Management

- The system shall allow users to create and maintain company profiles.
- The system shall allow users to associate multiple applications with one company.
- The system shall store company metadata including location, website, industry, and notes.

### Interview Management

- The system shall allow users to schedule interviews linked to an application.
- The system shall store interview type, round, date/time, location or meeting link, and preparation notes.
- The system shall trigger reminders for upcoming interviews and pending follow-ups.

### Reporting

- The system shall display summary metrics for applications by status.
- The system shall generate conversion metrics between key pipeline stages.
- The system shall allow export of filtered application records.

### Authentication and Access

- The system shall require authentication before accessing private user data.
- The system shall isolate each user's records from all other users by default.
- The system shall support role-based administrative access for support and reporting functions.

