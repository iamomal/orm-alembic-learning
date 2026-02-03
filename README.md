# ORM & Alembic Learning Project

A full-stack todo application demonstrating SQLAlchemy ORM, Alembic migrations, and relational database design.

## Features

- 🔐 Multi-user support
- 📋 Multiple todo lists per user (Home, School, Work, etc.)
- ✅ CRUD operations for users, lists, and items
- 🔄 Database migrations with Alembic
- 🎨 Clean, responsive UI

## Database Schema
```
User (1) ──→ (many) TodoList (1) ──→ (many) TodoItem
```

- **User**: Represents a user account
- **TodoList**: A named collection of todos (e.g., "Home", "School")
- **TodoItem**: Individual todo items within a list

## Tech Stack

**Backend:**
- Python 3.14
- FastAPI
- SQLAlchemy ORM
- Alembic (migrations)
- SQLite (development)

**Frontend:**
- Vanilla HTML/CSS/JavaScript
- Fetch API

## Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1  # Windows
pip install fastapi uvicorn sqlalchemy alembic
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

Open `frontend/index.html` in your browser.

## API Endpoints

### Users
- `POST /users/` - Create user
- `GET /users/` - List all users
- `GET /users/{user_id}` - Get user with their lists

### Lists
- `POST /users/{user_id}/lists/` - Create list for user
- `GET /users/{user_id}/lists/` - Get all lists for user
- `GET /lists/{list_id}` - Get list with items
- `DELETE /lists/{list_id}` - Delete list

### Items
- `POST /lists/{list_id}/items/` - Create item in list
- `GET /lists/{list_id}/items/` - Get all items in list
- `PATCH /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item

## Database Migrations

### Create a migration after changing models:
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### View migration history:
```bash
alembic history
```

### Rollback:
```bash
alembic downgrade -1
```

## Project Structure
```
orm-alembic-learning/
├── backend/
│   ├── alembic/
│   │   └── versions/          # Migration files
│   ├── app/
│   │   ├── models.py          # SQLAlchemy models (User, TodoList, TodoItem)
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── database.py        # DB connection
│   │   └── main.py            # FastAPI routes
│   └── alembic.ini
└── frontend/
    └── index.html             # Single-page app
```

## Learning Objectives

This project demonstrates:
- ✅ One-to-many relationships in SQLAlchemy
- ✅ Foreign key constraints
- ✅ Bidirectional relationships with `back_populates`
- ✅ Cascade deletes
- ✅ Database migration workflows
- ✅ RESTful API design
- ✅ Frontend-backend integration

## Example Usage
```python
# Create a user
user = User(username="warren", email="warren@example.com")

# Create lists for the user
home = TodoList(name="Home", user_id=user.id)
school = TodoList(name="School", user_id=user.id)

# Add items to lists
item1 = TodoItem(title="Buy groceries", list_id=home.id)
item2 = TodoItem(title="Study for exam", list_id=school.id)

# Navigate relationships
for todo_list in user.todo_lists:
    for item in todo_list.items:
        print(f"{item.title} in {todo_list.name}")
```