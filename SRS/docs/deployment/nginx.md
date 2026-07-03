# Nginx

## Responsibilities

- terminate TLS
- proxy requests to the application server
- serve static assets efficiently
- enforce request size and timeout boundaries

## Routing Outline

- `/static/` served directly
- `/media/` served according to storage strategy
- `/` proxied to Django or upstream app server

