# Auth Service

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.14-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE.md)
[![Tests](https://github.com/sendhello/auth-service/workflows/Tests/badge.svg)](https://github.com/sendhello/auth-service/actions)
[![CodeQL](https://github.com/sendhello/auth-service/actions/workflows/codeql.yml/badge.svg)](https://github.com/sendhello/auth-service/actions/workflows/codeql.yml)

A comprehensive authentication and authorization microservice built with FastAPI, designed for modern multi-tenant applications within the RooRoute platform.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Continuous Integration](#continuous-integration)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)
- [Authors](#authors)

## Features

- 🔐 **JWT Authentication**: Secure access and refresh token system with blacklisting
- 👤 **User Management**: Complete user lifecycle with registration, login, and profile management
- 🌐 **Google OAuth Integration**: Social login with automatic account creation
- 🏢 **Multi-tenant Architecture**: Organization-based user management and role separation
- 📊 **Login History Tracking**: Complete audit trail for user authentication events
- 🛡️ **Rate Limiting**: Configurable request throttling for API protection
- 📈 **Distributed Tracing**: OpenTelemetry integration with Jaeger monitoring
- 🚀 **High Performance**: Async/await throughout with Redis session management
- 📧 **Email Integration**: User verification and notification system
- 🔑 **Role-Based Access**: Admin and user role separation with scoped permissions

## Tech Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) 0.115.14
- **Language**: Python 3.13
- **Database**: PostgreSQL 15 with [SQLAlchemy](https://www.sqlalchemy.org/) (async)
- **Cache/Sessions**: Redis 7.2
- **Authentication**: JWT with async-fastapi-jwt-auth
- **OAuth**: Google OAuth 2.0 integration
- **Migration**: Alembic
- **Validation**: Pydantic v2
- **Tracing**: OpenTelemetry + Jaeger
- **Password Hashing**: Argon2
- **ASGI Server**: Uvicorn/Gunicorn
- **Containerization**: Docker & Docker Compose

## Architecture

The Auth Service acts as the central authentication provider for the RooRoute platform, issuing JWT tokens that other services use for authorization.

```
  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
  │   Client Apps   │    │   Web Client    │    │   Mobile Apps   │
  └─────────┬───────┘    └────────┬────────┘    └─────────┬───────┘
            │                     │                       │
            └─────────────────────┼───────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │      Auth Service         │
                    │   (FastAPI + JWT + OAuth) │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │    Order Service          │
                    │  (Consumes JWT tokens)    │
                    └───────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
    ┌─────────▼─────────┐ ┌───────▼────────┐ ┌────────▼─────────┐
    │   PostgreSQL      │ │     Redis      │ │   Other Services │
    │   (Order Data)    │ │    (Cache)     │ │ (Future Services)│
    └───────────────────┘ └────────────────┘ └──────────────────┘
```

### Service Integration

- **JWT Token Flow**: Auth Service issues tokens → Order Service validates tokens
- **User Context**: JWT tokens contain user ID and organization information
- **Shared Infrastructure**: Both services use Redis and Jaeger for optimal performance
- **Multi-tenant Support**: Organization-based isolation across all services

## Prerequisites

- **Python**: 3.13 or higher
- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher
- **PostgreSQL**: 15 or higher (if running locally)
- **Redis**: 7.2 or higher (if running locally)

## Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd auth-service
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and start services**
   ```bash
   docker compose up --build
   ```

The service will be available at `http://localhost:8000`

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd auth-service
   ```

2. **Create virtual environment**
   ```bash
   python3.13 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies with Poetry**
   ```bash
   poetry install --no-root
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   export $(grep -v -E '^\s*(#|$)' .env.local | xargs)
   ```

5. **Start infrastructure services**
   ```bash
   docker compose -f docker-compose-dev.yml up -d
   ```

6. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start the application**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Usage

### JWT Authentication Flow

```bash
# 1. Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'

# 2. Login to get JWT tokens
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'

# Response includes access_token and refresh_token
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "token_type": "Bearer"
# }

# 3. Use token to access protected endpoints
curl -X GET "http://localhost:8000/api/v1/profile" \
  -H "Authorization: Bearer <your-access-token>"

# 4. Use token with Order Service
curl -X POST "http://localhost:8001/api/v1/orders/" \
  -H "Authorization: Bearer <your-access-token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Package Delivery", ...}'
```

### Google OAuth Flow

```bash
# Initiate Google OAuth
curl -X POST "http://localhost:8000/api/v1/google/auth" \
  -H "Content-Type: application/json" \
  -d '{"code": "google-oauth-code-from-frontend"}'
```

## API Documentation

Once the service is running, you can access:

- **Swagger UI**: [http://localhost:8000/api/auth/openapi](http://localhost:8000/api/auth/openapi)
- **OpenAPI JSON**: [http://localhost:8000/api/auth/openapi.json](http://localhost:8000/api/auth/openapi.json)

### Main Endpoints

| Method | Endpoint                 | Description               | Auth Required |
|--------|--------------------------|---------------------------|---------------|
| `POST` | `/api/v1/auth/signup`    | User registration         | No            |
| `POST` | `/api/v1/auth/login`     | User login                | No            |
| `POST` | `/api/v1/auth/logout`    | User logout               | Yes           |
| `POST` | `/api/v1/auth/refresh`   | Refresh JWT token         | Yes           |
| `POST` | `/api/v1/google/auth`    | Google OAuth login        | No            |
| `GET`  | `/api/v1/verify/token`   | Verify JWT token validity | No            |
| `GET`  | `/api/v1/profile`        | Get user profile          | Yes           |
| `PUT`  | `/api/v1/profile`        | Update user profile       | Yes           |
| `GET`  | `/api/v1/users`          | List users (admin only)   | Admin         |
| `POST` | `/api/v1/users`          | Create user (admin only)  | Admin         |
| `GET`  | `/api/v1/organizations`  | List organizations        | Yes           |
| `POST` | `/api/v1/organizations`  | Create organization       | Yes           |

### Token Verification for Other Services

Other services (like Order Service) can verify JWT tokens using:

```bash
GET /api/v1/verify/token
Authorization: Bearer <jwt-token>
```

## Development

### Code Quality Tools

We use several tools to maintain code quality:

```bash
# Format code
black --skip-string-normalization .

# Sort imports
isort .

# Lint code (modern alternative to flake8)
ruff check .

# Type checking
mypy .

# Security scanning
bandit -r .
```

### Pre-commit Hooks

Install pre-commit hooks to ensure code quality:

```bash
pre-commit install
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade migration
alembic downgrade -1
```

### Project Structure

```
auth-service/
├── .github/                 # GitHub Actions workflows
│   └── workflows/           # CI/CD pipeline definitions
│       └── tests.yml        # Testing and security scanning
|       └── lint.yml         # Linting and type checking
|       └── security.yml     # Security scanning
|       └── types.yml        # Type checking
├── api/                     # API endpoints
│   └── v1/                  # API version 1
│       ├── auth.py          # Authentication endpoints
│       ├── google.py        # Google OAuth integration
│       ├── organizations.py # Organization management
│       ├── profile.py       # User profile management
│       ├── users.py         # User management (admin)
│       └── verify.py        # Token verification
├── core/                    # Core application configuration
│   ├── settings.py          # Application settings
│   ├── logger.py            # Logging configuration
│   └── tracer.py            # Jaeger tracing setup
├── db/                      # Database configuration
├── models/                  # SQLAlchemy models
├── schemas/                 # Pydantic schemas
├── security/                # Authentication & authorization
├── middleware/              # Custom middleware
├── migrations/              # Database migrations
├── tests/                   # Test suite
│   ├── functional/          # Functional/integration tests
│   └── test_basic.py        # Basic unit tests
├── LICENSE.md               # Apache 2.0 license
├── SECURITY.md              # Security policy and guidelines
├── README.md                # Project documentation
├── pyproject.toml           # Poetry configuration and dependencies
├── main.py                  # Application entry point
└── manage.py                # Management commands
```

## Testing

### Running Tests

```bash
# Run all tests
pytest -vv

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/functional/src/test_auth.py -v

# Run tests in parallel
pytest -n auto
```

### Test Structure

```
tests/
├── functional/             # API endpoint tests
│   ├── src/
│   │   ├── test_auth.py    # Authentication tests
│   │   ├── test_profile.py # Profile management tests
│   │   └── test_users.py   # User management tests
│   └── testdata/           # Test fixtures and data
├── test_basic.py           # Basic unit tests
└── conftest.py             # Test configuration
```

## Continuous Integration

The project uses GitHub Actions for automated testing and quality assurance. The CI pipeline runs on every push and pull request to `main` and `develop` branches.

### CI Pipeline Features

- **Automated Testing**: Runs full test suite with pytest
- **Code Quality**: Linting with Ruff, type checking with MyPy
- **Security Scanning**: Bandit security analysis
- **Code Coverage**: Coverage reporting with Codecov integration
- **Multi-environment**: Tests against PostgreSQL 15 and Redis 7.2
- **Poetry Integration**: Uses Poetry for dependency management

### Pipeline Jobs

1. **Test Job**: 
   - Sets up Python 3.13, PostgreSQL, and Redis
   - Installs dependencies with Poetry
   - Runs linting (ruff, mypy, bandit)
   - Executes test suite with coverage reporting

2. **Security Job**:
   - Performs security scanning with Bandit
   - Uploads security reports as artifacts

### Running Locally

To run the same checks locally as in CI:

```bash
# Install dependencies
poetry install --no-root

# Run linting
poetry run ruff check .
poetry run mypy .

# Run security scan
poetry run bandit -r . -f json

# Run tests with coverage
poetry run pytest tests/ -v --cov=. --cov-report=html
```

## Environment Variables

| Variable                               | Default             | Description                      |
|----------------------------------------|---------------------|----------------------------------|
| `AUTH_PROJECT_NAME`                    | `Auth`              | Service name (displayed in docs) |
| `DEBUG`                                | `false`             | Enable debug mode                |
| `POSTGRES_HOST`                        | `postgres`          | PostgreSQL hostname              |
| `POSTGRES_PORT`                        | `5432`              | PostgreSQL port                  |
| `POSTGRES_DB`                          | `auth`              | Database name                    |
| `POSTGRES_USER`                        | `app`               | PostgreSQL superuser             |
| `POSTGRES_PASSWORD`                    | -                   | PostgreSQL superuser password    |
| `POSTGRES_APP_USER`                    | `auth_app`          | Application database user        |
| `POSTGRES_APP_PASSWORD`                | -                   | Application database password    |
| `POSTGRES_MIGRATE_USER`                | `auth_owner`        | Migration database user          |
| `POSTGRES_MIGRATE_PASSWORD`            | -                   | Migration database password      |
| `REDIS_HOST`                           | `redis`             | Redis hostname                   |
| `REDIS_PORT`                           | `6379`              | Redis port                       |
| `ALLOW_EMPTY_PASSWORD`                 | `yes`               | Redis empty password setting     |
| `AUTHJWT_SECRET_KEY`                   | `secret`            | JWT signing secret               |
| `AUTHJWT_ACCESS_TOKEN_EXPIRES_MINUTES` | `15`                | Access token lifetime (minutes)  |
| `AUTHJWT_REFRESH_TOKEN_EXPIRES_DAYS`   | `30`                | Refresh token lifetime (days)    |
| `GOOGLE_CLIENT_ID`                     | -                   | Google OAuth client ID           |
| `GOOGLE_CLIENT_SECRET`                 | -                   | Google OAuth client secret       |
| `GOOGLE_REDIRECT_URI`                  | -                   | Google OAuth redirect URI        |
| `JAEGER_TRACE`                         | `true`              | Enable Jaeger tracing            |
| `JAEGER_AGENT_HOST`                    | `jaeger`            | Jaeger agent hostname            |
| `JAEGER_AGENT_PORT`                    | `6831`              | Jaeger agent port                |
| `REQUEST_LIMIT_PER_MINUTE`             | `20`                | Rate limit (requests per minute) |
| `ADMIN_PHONE`                          | `0000000000`        | Default admin phone number       |
| `ADMIN_EMAIL`                          | `admin@example.com` | Default admin email              |
| `ADMIN_PASSWORD`                       | -                   | Default admin password           |

### Default Admin User

A default superuser is automatically created during deployment:

- **Email**: admin@example.com
- **Password**: admin

⚠️ **Security Note**: Change the default admin credentials in production!

## Deployment

### Docker Production Build

```bash
# Build production image
docker build -t auth-service:latest .

# Run with production settings
docker run -d \
  --name auth-service \
  -p 8000:8000 \
  --env-file .env.prod \
  auth-service:latest
```

### System Requirements

- **Minimum**: 1 CPU, 1GB RAM
- **Recommended**: 2 CPU, 2GB RAM  
- **Storage**: 10GB for logs and database
- **Network**: Access to PostgreSQL, Redis, and Jaeger services

### Health Checks

- **Health endpoint**: `GET /health`
- **Database connection**: Automated health checks in docker-compose
- **Redis connectivity**: Connection validation on startup

## Security

Security is a top priority for the Auth Service. We follow industry best practices and maintain a comprehensive security policy.

### Security Features

- **Argon2 Password Hashing**: Industry-standard secure password hashing
- **JWT Token Management**: Stateless tokens with blacklisting capability
- **Rate Limiting**: Configurable request throttling (default: 20 req/min)
- **Input Validation**: Comprehensive validation using Pydantic
- **OAuth Security**: Secure Google OAuth 2.0 implementation
- **Database Security**: Minimal privilege database users
- **Session Management**: Redis-based secure session handling

### Security Policy

For detailed security information, vulnerability reporting, and best practices, please see our [Security Policy](SECURITY.md).

**Important**: 
- Never commit secrets to version control
- Use strong, unique secrets for `AUTHJWT_SECRET_KEY`
- Change default admin credentials in production
- Enable HTTPS in production environments
- Regularly update dependencies and security patches

### Reporting Security Issues

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: [bazhenov.in@gmail.com](mailto:bazhenov.in@gmail.com) with the subject `[SECURITY] Auth Service Vulnerability Report`.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Run code quality checks (`ruff check .`, `mypy .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Code Style Guidelines

- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for all public methods
- Maintain test coverage above 80%
- Use meaningful commit messages
- Add comprehensive tests for new features
- Update documentation for API changes

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details.

Copyright 2025 Ivan Bazhenov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Authors

- **Ivan Bazhenov** - *Initial work* - [@sendhello](https://github.com/sendhello)
  - Email: bazhenov.in@gmail.com

## Support

For support and questions:

- Create an issue on GitHub
- Check the [API documentation](http://localhost:8000/api/auth/openapi)
- Contact the maintainer via email
- Review existing issues for similar problems

---

**Built with ❤️ for the RooRoute platform using FastAPI and Python 3.13**