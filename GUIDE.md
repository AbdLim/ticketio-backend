# Developer's Guide to FastAPI Backend Template

This guide will help you understand how to use, configure, and extend this FastAPI backend template.

## Table of Contents

-   [Getting Started](#getting-started)
-   [Configuration](#configuration)
-   [Adding New Features](#adding-new-features)
-   [Database Management](#database-management)
-   [Authentication](#authentication)
-   [Caching](#caching)
-   [Testing](#testing)
-   [Deployment](#deployment)

## Getting Started

### 1. Initial Setup

1. Copy `example.env` to `.env` and update the variables:

    ```bash
    cp example.env .env
    ```

    Configure these essential environment variables:

    - `DATABASE_URL`: Your PostgreSQL connection string
    - `REDIS_URL`: Redis connection string
    - `SECRET_KEY`: JWT secret key
    - Other environment-specific variables

2. Install dependencies using UV:

    ```bash
    uv pip install .
    ```

3. For development dependencies:

    ```bash
    uv pip install -e ".[dev]"
    ```

4. Initialize the database:

    ```bash
    alembic upgrade head
    ```

5. Start the development server:
    ```bash
    uvicorn app.main:app --reload
    ```

### 2. Docker Setup

If using Docker:

1. Update `docker-compose.yaml` with your preferred configurations
2. Run:
    ```bash
    docker-compose up -d
    ```

## Configuration

### Environment Variables

Add new environment variables in three places:

1. `example.env` - Template for others
2. `app/core/config.py` - Add to Settings class
3. Your local `.env` file

Example adding a new configuration:

```python
# app/core/config.py
class Settings(BaseSettings):
    # ... existing settings ...
    NEW_SERVICE_URL: str = Field(..., env='NEW_SERVICE_URL')
```

## Adding New Features

### 1. Adding New API Endpoints

Location: `app/api/v1/`

1. Create a new router file (e.g., `app/api/v1/users.py`)
2. Structure your router:

```python
from fastapi import APIRouter, Depends
from app.api import deps

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def list_users():
    # Your endpoint logic here
    pass
```

3. Register in `app/api/v1/__init__.py`

### 2. Adding New Models

Location: `app/db/models/`

1. Create new model file (e.g., `app/db/models/user.py`)
2. Define your SQLModel:

```python
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    # ... other fields
```

3. Create migration: `alembic revision --autogenerate -m "Add user model"`

### 3. Adding New Schemas

Location: `app/schemas/`

1. Create schema file (e.g., `app/schemas/user.py`)
2. Define Pydantic models:

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
```

### 4. Adding New Services

Location: `app/services/`

1. Create service file (e.g., `app/services/user_service.py`)
2. Implement business logic:

```python
from app.db.repositories.base import BaseRepository

class UserService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    async def create_user(self, user_data):
        # Implementation
        pass
```

### 5. Adding New Repositories

Location: `app/db/repositories/`

1. Create repository file (e.g., `app/db/repositories/user_repository.py`)
2. Implement data access:

```python
from app.db.repositories.base import BaseRepository
from app.db.models.user import User

class UserRepository(BaseRepository):
    async def find_by_username(self, username: str):
        # Implementation
        pass
```

## Database Management

### Creating Migrations

1. Make changes to your SQLModel classes
2. Create migration:
    ```bash
    alembic revision --autogenerate -m "Description of changes"
    ```
3. Apply migration:
    ```bash
    alembic upgrade head
    ```

### Rolling Back

```bash
alembic downgrade -1  # Roll back one version
alembic downgrade base  # Roll back all migrations
```

## Authentication

### Implementing New Auth Methods

Location: `app/api/deps.py`

1. Add new dependency functions
2. Use in routes with FastAPI's dependency injection:

```python
@router.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    return {"message": "Access granted"}
```

## Caching

### Using Redis Cache

Location: `app/utils/cache.py`

1. Import cache utility:

```python
from app.utils.cache import cache

@cache(expires=300)  # Cache for 5 minutes
async def get_expensive_data():
    # Your implementation
    pass
```

## Testing

### Adding New Tests

Location: Create test files in parallel with source files

1. Example test structure:

```python
# tests/api/v1/test_users.py
import pytest
from httpx import AsyncClient

async def test_create_user(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/users",
        json={"username": "test", "email": "test@example.com"}
    )
    assert response.status_code == 200
```

### Running Tests

```bash
pytest  # Run all tests
pytest tests/api/v1/test_users.py  # Run specific test file
pytest -k "test_create"  # Run tests matching pattern
```

## Deployment

### Production Configuration

1. Update `Dockerfile` if needed
2. Set production environment variables
3. Build production image:
    ```bash
    docker build -t your-app-name .
    ```

### Production Best Practices

1. Use proper logging configuration in `app/core/logging.py`
2. Implement health checks
3. Set up monitoring
4. Configure CORS properly in `app/main.py`

## Common Tasks

### Adding Dependencies

1. Add to `pyproject.toml`:
    ```toml
    [project]
    dependencies = [
        "new-package>=1.0.0",
    ]
    ```
2. Update lockfile:
    ```bash
    uv pip compile pyproject.toml -o uv.lock
    ```

### Implementing Background Tasks

Location: `app/services/`

1. Create task file
2. Use FastAPI background tasks:

```python
from fastapi import BackgroundTasks

@router.post("/process")
async def process_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(your_background_task)
    return {"message": "Processing started"}
```

Remember to follow the established patterns and maintain consistency with the existing codebase when adding new features or making modifications.

For additional help or specific use cases, refer to:

-   FastAPI documentation: https://fastapi.tiangolo.com/
-   SQLModel documentation: https://sqlmodel.tiangolo.com/
-   Alembic documentation: https://alembic.sqlalchemy.org/
