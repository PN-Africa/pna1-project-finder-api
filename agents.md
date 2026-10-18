# AGENTS.md

## Project Overview
**Project Finder (PNA 1)** is a project simulation platform backend built with Django.
It provides an API backend for:
- **Learners / Users**: Discover project briefs, filter library items, review project scenarios and requirements, start simulations, upload and manage deliverables (upload, replace, delete), and submit completed simulations.
- **Administrators**: Manage users, create and edit project simulations, publish/unpublish projects, review submissions, and view dashboard metrics.

Reference specification: `dev-only/Project Finder Design Handoff Specification.docx`.

---

## Tech Stack & Environment
- **Runtime**: Python >= 3.14
- **Package Manager**: `uv`
- **Framework**: Django 6.1+
- **Database**: SQLite (default local development)
- **Virtual Environment**: `.venv`

### Common Commands
- **Run dev server**: `uv run python manage.py runserver`
- **Make migrations**: `uv run python manage.py makemigrations`
- **Apply migrations**: `uv run python manage.py migrate`
- **Run test suite**: `uv run python manage.py test`
- **Create admin user**: `uv run python manage.py createsuperuser`
- **Add dependencies**: `uv add <package>`

---

## Domain Models & State Lifecycle

### 1. Project (Simulation Brief)
- **Core Fields**:
  - `title` (string)
  - `industry` (enum/choice, filterable)
  - `difficulty` (enum/choice, filterable)
  - `short_description` (string, card preview)
  - Scenario details: `scenario`, `business_problem`, `objectives`, `stakeholders_team`, `context`, `role`, `tasks` (text)
  - `publication_status`: `Published` | `Unpublished`
- **Publication Rules**:
  - Only `Published` projects appear in the learner library.
  - `Unpublished` projects are accessible only to administrators.

### 2. Required Deliverable
- Belongs to a Project.
- Defines expected deliverable titles and guidelines (e.g., presentation, spreadsheet, report).

### 3. Simulation Attempt / Submission (Per User)
- Tracks a user's progress on a project.
- **Statuses**:
  - `Available`: Project is published; user has not yet started.
  - `In Progress`: User clicked "Start Project"; active simulation with editable deliverable files.
  - `Submitted`: Final submission completed; locked against further file uploads/modifications.
- **Tracking Fields**: `user`, `project`, `status`, `started_at`, `submitted_at`, `time_remaining`.

### 4. Deliverable Document (Uploaded File)
- Belongs to a Simulation Attempt and a Required Deliverable.
- Uploaded files persist across sessions.
- Users can upload, replace, or delete files while the simulation is `In Progress`.
- Read-only once the simulation reaches `Submitted`.

---

## Core API Scope

### User Endpoints
- `GET /api/projects/`: List published projects with filters (`industry`, `difficulty`), search, pagination, and user's status (`Available`, `In Progress`, `Submitted`).
- `GET /api/projects/<id>/`: Retrieve full project brief and required deliverables.
- `POST /api/projects/<id>/start/`: Start or resume a simulation (transitions to `In Progress`).
- `GET /api/simulations/<id>/`: Retrieve simulation state, time remaining, and uploaded files.
- `POST /api/simulations/<id>/deliverables/<deliverable_id>/upload/`: Upload or replace a deliverable document.
- `DELETE /api/simulations/<id>/deliverables/<deliverable_id>/`: Delete an uploaded deliverable document.
- `POST /api/simulations/<id>/submit/`: Validate all requirements and submit the simulation (transitions to `Submitted`).

### Admin Endpoints
- `GET /api/admin/dashboard/`: Dashboard summary metrics populated with real system data.
- `GET /api/admin/users/`: Search and filter user accounts.
- `GET|POST /api/admin/projects/`: List (all statuses) and create project simulations.
- `GET|PUT|PATCH|DELETE /api/admin/projects/<id>/`: Retrieve, edit, or publish/unpublish a project.
- `GET /api/admin/submissions/`: View and review user submissions.

---

## Agent Development Guidelines
- **API First**: Build clean RESTful views/viewsets with clear request/response contracts and status codes.
- **Immutability on Submission**: Enforce strict backend validation that disallows file uploads, updates, or deletions once an attempt is `Submitted`.
- **Authorization & Ownership**: Users may only access and alter their own simulation attempts and files. Admin views must enforce staff permissions.
- **File Management**: Handle file storage cleanly, validating allowed file formats and size constraints.
- **Maintain Documentation**: Keep models, serializers, and URL routes organized in focused Django apps (e.g., `projects`, `simulations`, `users`).
