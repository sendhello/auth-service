FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # poetry
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    \
    APP_PATH='/opt/app'

WORKDIR $APP_PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip && \
    pip install poetry==$POETRY_VERSION

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --only=main --no-root && \
    rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY . .

# Install the application
RUN poetry install --no-root

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R -g appuser appuser:appuser $APP_PATH
USER appuser

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "python manage.py migrate && python manage.py createsuperuser && gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"]