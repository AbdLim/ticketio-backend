# Ticketio Backend

A FastAPI-based backend service with SQLModel, Redis caching, and timezone-aware PostgreSQL.

## Prerequisites

-   Python 3.13+
-   PostgreSQL
-   Redis
-   uv (Python package manager)

## Quick Start

1. **Setup Environment**:

    ```bash
    # Create a virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate

    # Install dependencies
    uv venv
    uv pip install -e .
    ```

2. **Configure Environment**:

    ```bash
    cp example.env .env
    # Edit .env with your database and Redis credentials
    ```

3. **Setup Database**:

    ```bash
    createdb deebee  # Create PostgreSQL database
    uv run alembic upgrade head  # Run migrations
    ```

4. **Run the Application**:

    ```bash
    uv run dev
    ```

    Visit `http://localhost:8000/docs` for the API documentation.

## System Architecture

```
┌────────────────────┐
│    API Layer       │  FastAPI Routers
└─────────┬──────────┘
          │
┌─────────▼──────────┐
│  Service Layer     │  Business Logic & Caching
└─────────┬──────────┘
          │
┌─────────▼──────────┐
│ Repository Layer   │  Data Access
└─────────┬──────────┘
          │
┌─────────▼──────────┐
│  Database Layer    │  SQLModel/SQLAlchemy
└────────────────────┘
```

## Features

-   **FastAPI Framework**: High-performance async web framework
-   **SQLModel ORM**: Type-annotated database models
-   **Redis Caching**: Performance optimization
-   **Alembic Migrations**: Database versioning
-   **Timezone Support**: UTC-aware datetime handling
-   **CRUD Operations**: Generic repository pattern
-   **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Component Details

### 1. API Layer (Routers)

-   RESTful endpoint handlers
-   Input validation with Pydantic
-   Error handling and responses
-   OpenAPI documentation

### 2. Service Layer

-   Business logic implementation
-   Redis caching integration
-   Transaction coordination
-   Entity relationships

### 3. Repository Layer

-   Generic CRUD operations
-   Async database operations
-   Soft delete support
-   Query optimization

### 4. Database Layer

-   PostgreSQL with timezone support
-   SQLModel/SQLAlchemy integration
-   Connection pooling
-   Migration management

## API Documentation

-   Swagger UI: `http://localhost:8000/docs`
-   ReDoc: `http://localhost:8000/redoc`

## Development

See [GUIDE.md](GUIDE.md) for detailed development instructions.

## Security Architecture

-   JWT token-based authentication
-   OAuth 2.0 integration
-   Password hashing
-   Role-based access control (RBAC)
-   CORS protection
-   Rate limiting
-   Data encryption

## Error Handling

-   Standardized error responses
-   Detailed error logging
-   Graceful error recovery
-   Client-friendly error messages

## Logging and Monitoring

-   Structured logging
-   Request/Response logging
-   Error tracking
-   Performance monitoring
-   Audit logging for security events
