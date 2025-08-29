# Auth Service

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.14-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

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
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
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

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or if using poetry
   poetry install
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
├── api/                    # API endpoints
│   └── v1/                # API version 1
│       ├── auth.py        # Authentication endpoints
│       ├── google.py      # Google OAuth integration
│       ├── organizations.py # Organization management
│       ├── profile.py     # User profile management
│       ├── users.py       # User management (admin)
│       └── verify.py      # Token verification
├── core/                  # Core application configuration
│   ├── settings.py        # Application settings
│   ├── logger.py          # Logging configuration
│   └── tracer.py          # Jaeger tracing setup
├── db/                    # Database configuration
├── models/                # SQLAlchemy models
├── schemas/               # Pydantic schemas
├── security/              # Authentication & authorization
├── middleware/            # Custom middleware
├── migrations/            # Database migrations
├── main.py                # Application entry point
└── manage.py              # Management commands
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
├── functional/            # API endpoint tests
│   ├── src/
│   │   ├── test_auth.py   # Authentication tests
│   │   ├── test_profile.py # Profile management tests
│   │   └── test_users.py  # User management tests
│   └── testdata/          # Test fixtures and data
└── conftest.py            # Test configuration
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `PROJECT_NAME` | `Auth Service` | Service name (displayed in docs) |
| `POSTGRES_HOST` | `localhost` | PostgreSQL hostname |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_DB` | `auth` | Database name |
| `POSTGRES_APP_USER` | `app` | Application database user |
| `POSTGRES_APP_PASSWORD` | - | Application database password |
| `REDIS_HOST` | `localhost` | Redis hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `AUTHJWT_SECRET_KEY` | `secret` | JWT signing secret |
| `AUTHJWT_ACCESS_TOKEN_EXPIRES_MINUTES` | `15` | Access token lifetime (minutes) |
| `AUTHJWT_REFRESH_TOKEN_EXPIRES_DAYS` | `30` | Refresh token lifetime (days) |
| `GOOGLE_CLIENT_ID` | - | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | - | Google OAuth client secret |
| `GOOGLE_REDIRECT_URI` | - | Google OAuth redirect URI |
| `JAEGER_TRACE` | `false` | Enable Jaeger tracing |
| `JAEGER_AGENT_HOST` | `localhost` | Jaeger agent hostname |
| `JAEGER_AGENT_PORT` | `6831` | Jaeger agent port |
| `REQUEST_LIMIT_PER_MINUTE` | `20` | Rate limit (requests per minute) |

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

This project is part of the RooRoute platform. All rights reserved.

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