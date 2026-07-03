# Folder Structure

```text
job-tracker/
  manage.py
  config/
    settings/
    urls.py
    wsgi.py
    asgi.py
  apps/
    core/
    accounts/
    companies/
    applications/
    interviews/
    reports/
  templates/
  static/
  tests/
  requirements/
  docker/
```

## Conventions

- project configuration lives under `config/`
- business apps live under `apps/`
- shared test helpers live under `tests/`
- environment-specific settings are split by module

