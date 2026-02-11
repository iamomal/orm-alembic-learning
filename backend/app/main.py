from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from app.database import get_db
from app.models import User, TodoList, TodoItem
from app.schemas import (
    UserRegister, UserLogin, Token, UserResponse, UserWithLists,
    TodoListCreate, TodoListResponse, TodoListWithItems,
    TodoItemCreate, TodoItemUpdate, TodoItemResponse
)
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="Todo API with Supabase")

# FIXED: Allow both localhost and 127.0.0.1
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5501",
    "http://localhost:5501",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
]

# CORS - with explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ============ Auth Endpoints ============

@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/auth/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    # Find user
    db_user = db.query(User).filter(User.username == user.username).first()
    
    # Verify credentials
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current logged-in user"""
    return current_user


# ============ TodoList Endpoints (Protected) ============

@app.post("/lists/", response_model=TodoListResponse, status_code=201)
def create_todo_list(
    todo_list: TodoListCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new todo list for the current user"""
    new_list = TodoList(**todo_list.model_dump(), user_id=current_user.id)
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    return new_list


@app.get("/lists/", response_model=List[TodoListWithItems])
def get_my_lists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all lists for the current user"""
    return db.query(TodoList).filter(TodoList.user_id == current_user.id).all()


@app.get("/lists/{list_id}", response_model=TodoListWithItems)
def get_todo_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific todo list (must be owned by current user)"""
    todo_list = db.query(TodoList).filter(
        TodoList.id == list_id,
        TodoList.user_id == current_user.id
    ).first()
    
    if not todo_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    return todo_list


@app.delete("/lists/{list_id}", status_code=204)
def delete_todo_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a todo list (must be owned by current user)"""
    todo_list = db.query(TodoList).filter(
        TodoList.id == list_id,
        TodoList.user_id == current_user.id
    ).first()
    
    if not todo_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    db.delete(todo_list)
    db.commit()
    return None


# ============ TodoItem Endpoints (Protected) ============

@app.post("/lists/{list_id}/items/", response_model=TodoItemResponse, status_code=201)
def create_todo_item(
    list_id: int,
    item: TodoItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new todo item (list must be owned by current user)"""
    # Verify list belongs to current user
    todo_list = db.query(TodoList).filter(
        TodoList.id == list_id,
        TodoList.user_id == current_user.id
    ).first()
    
    if not todo_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    new_item = TodoItem(**item.model_dump(), list_id=list_id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@app.patch("/items/{item_id}", response_model=TodoItemResponse)
def update_todo_item(
    item_id: int,
    item_update: TodoItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a todo item (must be in user's list)"""
    item = db.query(TodoItem).join(TodoList).filter(
        TodoItem.id == item_id,
        TodoList.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item_update.title is not None:
        item.title = item_update.title
    if item_update.completed is not None:
        item.completed = item_update.completed
    
    db.commit()
    db.refresh(item)
    return item


@app.delete("/items/{item_id}", status_code=204)
def delete_todo_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a todo item (must be in user's list)"""
    item = db.query(TodoItem).join(TodoList).filter(
        TodoItem.id == item_id,
        TodoList.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return None