# Job Tracker Documentation

This site is the central documentation hub for the Job Tracker platform. It combines product requirements, system design, user interface specifications, API contracts, deployment guidance, and roadmap planning into a single navigable knowledge base.

## Purpose

Job Tracker helps users manage the full job-search lifecycle in one place:

- track job applications and their statuses
- organize companies, contacts, and notes
- manage interview scheduling and follow-up tasks
- generate reports and analytics on search performance
- maintain a repeatable, searchable application pipeline

## Document set

This documentation is structured to support multiple audiences:

- product stakeholders need business goals, scope, and release planning
- developers need architecture, models, APIs, and folder conventions
- QA needs acceptance criteria and testing strategy
- DevOps needs deployment, configuration, and production guidance

## Assumptions

The initial target implementation assumes:

- a Django backend with Django REST Framework
- PostgreSQL as the primary relational database
- a web frontend rendered either by Django templates or a separate SPA
- Docker-based local development and production packaging
- role-based access controls with a single-tenant default architecture

## Reading order

If you are new to the project, start with:

1. Vision
2. Requirements
3. Architecture
4. API
5. Deployment

