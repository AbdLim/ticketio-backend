from sqlmodel import SQLModel
from app.db.models.todo import Todo
from app.db.models.user import User

__all__ = [
    "Todo",
    "User",
    "SQLModel",  # Export SQLModel to ensure metadata is registered
]

# Ensure models are registered with SQLModel's metadata
Todo.metadata
