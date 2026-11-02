# Project Finder API

A RESTful API built with Django and Django REST Framework for managing, discovering, and running simulations for projects. It features authentication, customizable user profiles, project filtering, and file deliverable tracking.

---

## Features

- **User Authentication & Management**
  - Custom User model supporting email-based authentication.
  - Integration with dj-rest-auth and django allauth for registration, email confirmation, and password reset workflows.
- **Project Finder Core**
  - Create, update, view, and delete project listings with detailed briefs.
  - Advanced filtering and searching (powered by `django-filter`).
  - Custom pagination for efficient data retrieval.
- **Deliverable Submissions**
  - File uploads for project deliverables.
- **Developer Experience**
  - Environment-based configuration (`dev`, `prod`, `common`).
  - Managed with [uv](https://github.com/astral-sh/uv) for fast package resolution.
  - Automated testing with `pytest`.

---

## Tech Stack

- **Language:** Python 3.14+
- **Framework:** Django 5+
- **API Engine:** Django REST Framework (DRF)
- **Authentication:** Django Allauth / dj-rest-auth
- **Package Manager:** `uv`
- **Testing:** `pytest`, `pytest-django`
- **Database:** PostgreSQL (Production) / SQLite (Development)

---

## Project Structure

```text
project-finder/
├── accounts/               # Custom user management, auth views & serializers
├── core/                   # Shared utilities, base models, pagination helpers
├── projectfinder/          # Project configuration settings (common, dev, prod), ASGI/WSGI
│   └── settings/
│       ├── common.py
│       ├── dev.py
│       └── prod.py
├── projects/               # Projects and simulations logic, filters, views & serializers
├── templates/              # Text templates for auth emails
├── tests/                  # Integration and unit tests
├── .env.example            # Environment variables template
├── manage.py               # Django management entry point
└── pyproject.toml          # Project dependencies and tool configurations
```

---

## Getting Started

### Prerequisites

- Python 3.14 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or standard `pip`

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/project-finder.git
cd project-finder
```

### 2. Set Up Virtual Environment & Dependencies

Using `uv` (recommended):

```bash
uv sync
```

Using standard Python `venv`:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### 3. Environment Configuration

Copy the example environment file and adjust setting values as needed:

```bash
cp .env.example .env
```

Ensure your `.env` contains the required keys (such as `DJANGO_SECRET_KEY`, database settings, etc).

### 4. Database Setup & Migrations

Apply database migrations:

```bash
python manage.py migrate
```

Create a superuser to access the Django Admin portal:

```bash
python manage.py createsuperuser
```

### 5. Run the Server

Start the local development server:

```bash
python manage.py runserver --settings=projectfinder.settings.dev
```

The API will be available at `http://127.0.0.1:8000/`.

---

## API Endpoints Overview

| Endpoint Pattern     | Description                                                      |
| :------------------- | :--------------------------------------------------------------- |
| `/api/auth/*`        | Register, login, retrieve/update user profile, etc               |
| `/api/projects/*`    | List, filter, and retrieve projects                              |
| `/api/simulations/*` | List, retrieve, start & submit simulations, upload deliverables  |
| `/api/admin/*`       | Project, simulation, and user management by administrative users |

A Detailed API documentation can be obtained by running the development server and accessing `/api/docs/`
