# Models

## Core Entities

### Company

- `id`
- `owner`
- `name`
- `website`
- `industry`
- `location`
- `notes`
- `created_at`
- `updated_at`

### Application

- `id`
- `owner`
- `company`
- `title`
- `department`
- `source`
- `status`
- `salary_min`
- `salary_max`
- `currency`
- `applied_at`
- `notes`
- `archived`

### Interview

- `id`
- `application`
- `interview_type`
- `round_name`
- `scheduled_at`
- `duration_minutes`
- `location`
- `meeting_url`
- `notes`
- `outcome`

## Supporting Entities

- `Contact`
- `FollowUp`
- `ApplicationStatusHistory`
- `Tag`
- `SavedFilter`

