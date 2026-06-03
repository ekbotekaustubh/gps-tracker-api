# GPS Tracker API

A Flask-based REST API for a GPS Tracker Management System — track GPS devices, manage organizations and branches, assign devices to members, and monitor real-time locations. Containerized with Docker and backed by MySQL.

## Project Structure

```
api/v1/
├── compose.yaml           # Docker Compose (Flask + MySQL + phpMyAdmin)
├── Dockerfile             # Flask app container
├── manage.py              # CLI: test, cov, create_db, drop_db
├── run_app.py             # Dev server with DB retry logic
├── wsgi.py                # WSGI entry point (production)
├── requirements.txt       # Python dependencies
│
├── database/
│   ├── Dockerfile         # MySQL image + init script
│   └── mysql-init.sql     # Schema (12 tables) + seed data
│
└── src/
    ├── server/
    │   ├── __init__.py    # Flask app, API setup, namespace registration
    │   ├── config.py      # Multi-env config (Dev / Test / Production)
    │   ├── models/        # SQLAlchemy models (one file per table)
    │   │   ├── user.py
    │   │   ├── blacklist_token.py
    │   │   ├── country.py
    │   │   ├── state.py
    │   │   ├── city.py
    │   │   ├── organization.py
    │   │   ├── branch.py
    │   │   ├── role.py
    │   │   ├── permission.py
    │   │   ├── role_permission.py
    │   │   ├── card.py
    │   │   ├── card_member.py
    │   │   └── location.py
    │   └── auth/
    │       ├── views.py   # Register, Login, Logout, User endpoints
    │       └── utility.py # check_login decorator
    │
    └── tests/
        ├── base.py        # BaseTestCase
        ├── test__config.py
        ├── test_auth.py
        └── test_user_model.py
```

## Database Schema

The system uses **12 tables** across these domains:

| Domain | Tables |
|---|---|
| **Geography** | `countries`, `states`, `cities` |
| **Organization** | `organizations`, `branches` |
| **Access Control** | `users`, `roles`, `permissions`, `role_permissions`, `blacklist_tokens` |
| **GPS Tracking** | `cards` (devices), `card_members`, `locations` |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd gps-tracker-app/api/v1
```

### 2. Run the application with Docker

```bash
docker compose up -d --build
```

This will start three services:

| Service | Port | Description |
|---|---|---|
| **backend** | `5000` | Flask API server |
| **mysql** | `3306` | MySQL database |
| **phpmyadmin** | `8080` | Database admin UI |

### 3. Access the application

- **Swagger API Docs:** [http://localhost:5000/docs](http://localhost:5000/docs)
- **Health Check:** [http://localhost:5000/health](http://localhost:5000/health)
- **phpMyAdmin:** [http://localhost:8080](http://localhost:8080)

## Database Configuration

### Default Credentials

| Setting | Value |
|---|---|
| **Host** | `mysql` (Docker network) / `localhost` (host machine) |
| **Port** | `3306` |
| **Username** | `root` |
| **Password** | `toor` |
| **Database** | `gps_tracker` |

### Creating Database Tables

Tables are automatically created from `mysql-init.sql` on first run. To recreate via SQLAlchemy:

```bash
docker compose exec backend python manage.py create_db
```

## Running Tests

Run unit tests:

```bash
docker compose exec backend python manage.py test
```

Run tests with coverage:

```bash
docker compose exec backend python manage.py cov
```

## Local Development (without Docker)

1. Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set the configuration (optional — defaults to MySQL production):
    ```bash
    export APP_SETTINGS="src.server.config.DevelopmentConfig"
    ```

4. Run the dev server:
    ```bash
    python run_app.py
    ```

## API Endpoints

All endpoints are prefixed with `/api/v1` and documented via Swagger at `/docs`.

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive JWT token |
| `POST` | `/auth/logout` | Logout and blacklist token |
| `GET` | `/auth/user` | Get authenticated user info |
| `GET` | `/auth/refresh` | Refresh authentication |

### Authentication Header

Protected endpoints require a Bearer token:

```
Authorization: Bearer <your-jwt-token>
```

## Tech Stack

- **Framework:** Flask 2.3 + Flask-RESTX (Swagger)
- **Database:** MySQL with SQLAlchemy ORM
- **Auth:** JWT (PyJWT) + Bcrypt password hashing
- **Containerization:** Docker + Docker Compose
- **Python:** 3.10
