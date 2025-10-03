# Development Guide

## Prerequisites

-   Python 3.13+
-   PostgreSQL
-   Redis
-   uv (Python package manager)

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd ticketio-backend
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install dependencies using uv:

```bash
uv venv
uv pip install -e .
```

4. Copy example.env to .env and configure:

```bash
cp example.env .env
# Edit .env with your database and Redis credentials
```

## Database Setup

1. Create a PostgreSQL database:

```bash
createdb deebee
```

2. Run migrations:

```bash
uv run alembic upgrade head
```

## Running the Application

1. Start Redis:

```bash
redis-server
```

2. Start the application:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

-   OpenAPI (Swagger) UI: `http://localhost:8000/docs`
-   ReDoc: `http://localhost:8000/redoc`

## Development

### Project Structure

```
app/
├── api/             # API endpoints
├── core/            # Core configuration
├── db/              # Database models and repositories
├── schemas/         # Pydantic schemas
├── services/        # Business logic
└── utils/           # Utilities and helpers
```

### Key Components

1. **Models**

    - Located in `app/db/models/`
    - Use SQLModel for defining database tables

2. **Schemas**

    - Located in `app/schemas/`
    - Pydantic models for request/response validation

3. **Repositories**

    - Located in `app/db/repositories/`
    - Handle database operations
    - Implement generic CRUD operations

4. **Services**

    - Located in `app/services/`
    - Implement business logic
    - Handle caching and complex operations

5. **API Routes**
    - Located in `app/api/`
    - Define HTTP endpoints
    - Handle request/response formatting

### Adding New Features

1. **Create a Model**:

    ```python
    # app/db/models/your_model.py
    from app.db.base import Base

    class YourModel(Base):
        __tablename__ = "your_table"
        # Define fields
    ```

2. **Create Schemas**:

    ```python
    # app/schemas/your_schema.py
    from pydantic import BaseModel

    class YourModelCreate(BaseModel):
        # Define creation fields
    ```

3. **Create Repository**:

    ```python
    # app/db/repositories/your_repository.py
    from app.db.repositories.base import BaseRepository
    from app.db.models.your_model import YourModel

    class YourRepository(BaseRepository[YourModel]):
        pass
    ```

4. **Create Service**:

    ```python
    # app/services/your_service.py
    from app.services.base import BaseService

    class YourService(BaseService):
        # Implement business logic
    ```

5. **Create API Routes**:

    ```python
    # app/api/v1/your_routes.py
    from fastapi import APIRouter, Depends

    router = APIRouter()

    @router.post("/")
    async def create_item():
        # Implement endpoint
    ```

### Working with Database Migrations

1. Create a new migration:

```bash
uv run alembic revision --autogenerate -m "description"
```

2. Apply migrations:

```bash
uv run alembic upgrade head
```

3. Rollback migration:

```bash
uv run alembic downgrade -1
```

## Testing

1. Run tests:

```bash
uv run pytest
```

2. Run with coverage:

```bash
uv run pytest --cov=app
```

## Caching

The application uses Redis for caching:

-   Individual items are cached with their ID as key
-   List endpoints have separate cache keys
-   Cache is automatically invalidated on updates
-   Default TTL is 1 hour

## Error Handling

-   HTTP exceptions are handled by FastAPI
-   Custom exceptions are defined in `app/core/exceptions.py`
-   Validation errors return 422 status code
-   Database errors are caught and returned as 500

## Timezone Handling

All datetime fields in the database are stored with timezone information:

-   `created_at`, `updated_at`, `deleted_at`: Automatically managed timestamp fields
-   `due_date`: User-specified datetime for todos
-   All times are stored in UTC
-   API responses include timezone information
-   Migrations ensure proper timezone support in PostgreSQL

## Repository Pattern

The application uses a generic repository pattern:

-   `BaseRepository`: Generic CRUD operations
-   Type-safe with SQLModel
-   Soft delete support
-   Async operations
-   Query optimization

Example repository usage:

```python
# Define a repository
class TodoRepository(BaseRepository[Todo]):
    pass

# Use in a service
class TodoService:
    def __init__(self, repository: TodoRepository):
        self.repository = repository

    async def get_todo(self, id: int) -> Optional[Todo]:
        return await self.repository.get_by_id(id)
```
