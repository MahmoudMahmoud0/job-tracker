# Django Apps

## Proposed App Boundaries

| App | Responsibility |
| --- | --- |
| `accounts` | authentication, profile, preferences |
| `companies` | company records and related contacts |
| `applications` | job applications, statuses, notes |
| `interviews` | interview scheduling, reminders, feedback |
| `reports` | metrics, aggregations, exports |
| `core` | shared utilities, base models, audit helpers |

## Design Notes

- `applications` owns the main pipeline entity.
- `companies` is a reusable directory rather than a nested submodule.
- `reports` should mostly read from other apps and avoid owning core source-of-truth records.

