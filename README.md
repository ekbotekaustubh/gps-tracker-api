# Pathology Lab API

A Flask-based backend application for a pathology laboratory management system, containerized with Docker and using MySQL.

## Project Structure

- `src/`: Application source code
  - `server/`: Flask app, models, and routes
  - `tests/`: Unit and integration tests
- `database/`: MySQL database initialization and configuration
- `Dockerfile`: Container definition for the Flask application
- `compose.yaml`: Docker Compose configuration for the entire stack
- `manage.py`: CLI utility for managing the application and database

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd gps-tracker-api
```

### 2. Run the application with Docker

The project uses Docker Compose to manage both the Flask application and the MySQL database.

```bash
docker compose up -d --build
```

This will:
- Build the Flask application image.
- Start a MySQL container (named `mysql`).
- Start the Flask application (named `backend`) on port `5000`.

### 3. Access the API

- **Swagger Documentation:** [http://localhost:5000/docs](http://localhost:5000/docs)
- **Health Check:** [http://localhost:5000/health](http://localhost:5000/health)

## Database Management

The application is configured to use MySQL in production.

### Database Credentials (Default)

- **Host:** `mysql` (inside Docker network) or `localhost` (from host machine)
- **Port:** `3306`
- **Username:** `root`
- **Password:** `toor`
- **Database:** `test`

### Creating Database Tables

If the tables are not created automatically, you can run:

```bash
docker compose exec backend python manage.py create_db
```

## Running Tests

To run the unit tests:

```bash
docker compose exec backend python manage.py test
```

To run tests with coverage:

```bash
docker compose exec backend python manage.py cov
```

## Development

If you want to run the application locally (without Docker):

1.  Create a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set the `APP_SETTINGS` environment variable (optional, defaults to MySQL production):
    ```bash
    export APP_SETTINGS="src.server.config.DevelopmentConfig"
    ```
4.  Run the app:
    ```bash
    python manage.py run
    ```

## API Endpoints

The API is organized into several namespaces:
- `/auth`: Authentication (Login, Register, Status)
- `/patient`: Patient records management
- `/test`: Pathology test management
- `/profile`: User and laboratory profiles
- `/package`: Test packages
- ... and more.

Refer to the Swagger documentation at `/docs` for full details.
