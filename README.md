# RooRoute Auth Service

A comprehensive authentication and authorization microservice built with FastAPI, designed for modern multi-tenant applications.

## 🚀 Features

### Core Authentication
- **JWT-based Authentication** - Secure access and refresh token system
- **User Registration & Login** - Email-based user accounts with password hashing
- **Google OAuth Integration** - Social login with automatic account creation
- **Token Management** - Automatic token refresh and secure logout with blacklisting

### Enterprise Features
- **Multi-tenancy Support** - Organization-based user management and role separation
- **User Profile Management** - Comprehensive user data and profile endpoints
- **Login History Tracking** - Audit trail for user authentication events
- **Rate Limiting** - Configurable request throttling for API protection

### Security & Observability
- **Request ID Middleware** - Distributed tracing support
- **Jaeger Integration** - Complete observability and performance monitoring
- **Redis Session Management** - Fast token storage and blacklisting
- **Comprehensive Validation** - Input validation and error handling

### Development & Operations
- **Docker Support** - Production and development containerization
- **Database Migrations** - Alembic-based schema management
- **Comprehensive Testing** - Full test suite with functional tests
- **API Documentation** - Auto-generated OpenAPI/Swagger documentation

## 🏗️ Architecture

### Tech Stack
- **Framework:** FastAPI (Python 3.13)
- **Database:** PostgreSQL with AsyncPG
- **Cache/Sessions:** Redis
- **Authentication:** JWT with async-fastapi-jwt-auth
- **ORM:** SQLAlchemy (async)
- **Validation:** Pydantic v2
- **Testing:** Pytest
- **Containerization:** Docker & Docker Compose

### Project Structure
```
auth-service/
├── api/                    # API endpoints and routing
│   └── v1/                # API version 1
│       ├── auth.py        # Authentication endpoints
│       ├── google.py      # Google OAuth integration
│       ├── organizations.py # Organization management
│       ├── profile.py     # User profile management
│       └── users.py       # User management
├── core/                  # Core application configuration
│   ├── settings.py        # Application settings
│   ├── logger.py          # Logging configuration
│   └── tracer.py          # Jaeger tracing setup
├── db/                    # Database configuration
├── models/                # SQLAlchemy models
├── schemas/               # Pydantic schemas
├── security/              # Security utilities
├── middleware/            # Custom middleware
├── migrations/            # Database migrations
└── tests/                 # Test suite
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.13+ (for local development)
- PostgreSQL 13+
- Redis 6+

### Production Deployment
```bash
# Clone the repository
git clone git@github.com:sendhello/auth-service.git
cd auth-service

# Start all services
docker compose up --build
```

The service will be available at:
- **API:** http://localhost:8000/api
- **Documentation:** http://localhost:8000/api/auth/openapi
- **OpenAPI JSON:** http://localhost:8000/api/auth/openapi.json

### Development Setup
```bash
# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start infrastructure services
docker compose -f docker-compose-dev.yml up -d

# Run database migrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser

# Start the development server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Token refresh

### Google OAuth
- `POST /api/v1/google/auth` - Initiate Google OAuth flow
- `GET /api/v1/google/auth_return` - OAuth callback endpoint

### User Management
- `GET /api/v1/profile` - Get user profile
- `PUT /api/v1/profile` - Update user profile
- `GET /api/v1/users` - List users (admin)
- `POST /api/v1/users` - Create user (admin)

### Organizations
- `GET /api/v1/organizations` - List organizations
- `POST /api/v1/organizations` - Create organization
- `GET /api/v1/organizations/{id}/members` - List organization members

For complete API documentation, visit the Swagger UI at `/api/auth/openapi` when the service is running.

## ⚙️ Configuration

### Environment Variables

| Variable                               | Default     | Description                      |
|----------------------------------------|-------------|----------------------------------|
| `DEBUG`                                | `False`     | Enable debug mode                |
| `PROJECT_NAME`                         | `Auth`      | Service name (shown in API docs) |
| `REDIS_HOST`                           | `127.0.0.1` | Redis server hostname            |
| `REDIS_PORT`                           | `6379`      | Redis server port                |
| `POSTGRES_HOST`                        | `localhost` | PostgreSQL hostname              |
| `POSTGRES_PORT`                        | `5432`      | PostgreSQL port                  |
| `POSTGRES_DB`                          | `auth`      | Database name                    |
| `POSTGRES_APP_USER`                    | `app`       | Application database user        |
| `POSTGRES_APP_PASSWORD`                | -           | Application database password    |
| `AUTHJWT_SECRET_KEY`                   | `secret`    | JWT signing secret               |
| `AUTHJWT_ACCESS_TOKEN_EXPIRES_MINUTES` | `15`        | Access token lifetime            |
| `AUTHJWT_REFRESH_TOKEN_EXPIRES_DAYS`   | `30`        | Refresh token lifetime           |
| `GOOGLE_CLIENT_ID`                     | -           | Google OAuth client ID           |
| `GOOGLE_CLIENT_SECRET`                 | -           | Google OAuth client secret       |
| `GOOGLE_REDIRECT_URI`                  | -           | Google OAuth redirect URI        |
| `JAEGER_TRACE`                         | `True`      | Enable Jaeger tracing            |
| `JAEGER_AGENT_HOST`                    | `localhost` | Jaeger agent hostname            |
| `JAEGER_AGENT_PORT`                    | `6831`      | Jaeger agent port                |
| `REQUEST_LIMIT`                        | `20`        | Rate limit (requests per minute) |

### Default Superuser
A default superuser is automatically created:
- **Email:** admin@example.com
- **Password:** admin

## 🧪 Testing

### Run Tests
```bash
# Install development dependencies
poetry install --with dev

# Run all tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/functional/ -v
```

### Code Quality
```bash
# Format code
black --skip-string-normalization .
isort .

# Lint code
flake8 .

# Type checking
mypy .
```

## 🔧 Development

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Adding New Features
1. Create feature branch from `main`
2. Add/modify models in `models/`
3. Create/update schemas in `schemas/`
4. Implement API endpoints in `api/v1/`
5. Add tests in `tests/`
6. Update documentation
7. Submit pull request

## 📊 Monitoring

### Health Checks
- **Health endpoint:** `GET /health`
- **Metrics:** Integrated with Jaeger for distributed tracing
- **Logging:** Structured JSON logging with request IDs

### Performance
- **Redis caching** for session management
- **Connection pooling** for database operations
- **Async/await** throughout the application
- **Rate limiting** to prevent abuse

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive tests for new features
- Update documentation for API changes
- Use conventional commit messages

## 📝 License

This project is part of the RooRoute platform.

## 👥 Maintainers

- **Ivan Bazhenov** - [@sendhello](https://github.com/sendhello)

## 🆘 Support

For support and questions:
1. Check the [API documentation](http://localhost:8000/api/auth/openapi)
2. Review existing [issues](../../issues)
3. Create a new issue with detailed description

---

**Built with ❤️ for the RooRoute platform**
