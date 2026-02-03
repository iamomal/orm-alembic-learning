from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, TodoList, TodoItem, ToDo
from app.schemas import (
    UserCreate, UserResponse, UserWithLists,
    TodoListCreate, TodoListResponse, TodoListWithItems,
    TodoItemCreate, TodoItemUpdate, TodoItemResponse,
    ToDoCreate, ToDoUpdate, ToDoResponse
)

app = FastAPI(title="Todo API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ User Endpoints ============

@app.post("/users/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.get("/users/{user_id}", response_model=UserWithLists)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============ TodoList Endpoints ============

@app.post("/users/{user_id}/lists/", response_model=TodoListResponse, status_code=201)
def create_todo_list(user_id: int, todo_list: TodoListCreate, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_list = TodoList(**todo_list.model_dump(), user_id=user_id)
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    return new_list


@app.get("/users/{user_id}/lists/", response_model=List[TodoListResponse])
def get_user_lists(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(TodoList).filter(TodoList.user_id == user_id).all()


@app.get("/lists/{list_id}", response_model=TodoListWithItems)
def get_todo_list(list_id: int, db: Session = Depends(get_db)):
    todo_list = db.query(TodoList).filter(TodoList.id == list_id).first()
    if not todo_list:
        raise HTTPException(status_code=404, detail="List not found")
    return todo_list


@app.delete("/lists/{list_id}", status_code=204)
def delete_todo_list(list_id: int, db: Session = Depends(get_db)):
    todo_list = db.query(TodoList).filter(TodoList.id == list_id).first()
    if not todo_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    db.delete(todo_list)  # This will also delete all items (cascade)
    db.commit()
    return None


# ============ TodoItem Endpoints ============

@app.post("/lists/{list_id}/items/", response_model=TodoItemResponse, status_code=201)
def create_todo_item(list_id: int, item: TodoItemCreate, db: Session = Depends(get_db)):
    # Check if list exists
    todo_list = db.query(TodoList).filter(TodoList.id == list_id).first()
    if not todo_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    new_item = TodoItem(**item.model_dump(), list_id=list_id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@app.get("/lists/{list_id}/items/", response_model=List[TodoItemResponse])
def get_list_items(list_id: int, db: Session = Depends(get_db)):
    todo_list = db.query(TodoList).filter(TodoList.id == list_id).first()
    if not todo_list:
        raise HTTPException(status_code=404, detail="List not found")
    return db.query(TodoItem).filter(TodoItem.list_id == list_id).all()


@app.patch("/items/{item_id}", response_model=TodoItemResponse)
def update_todo_item(item_id: int, item_update: TodoItemUpdate, db: Session = Depends(get_db)):
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
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
def delete_todo_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return None


# ============ Old Todo Endpoints (backward compatibility) ============

@app.post("/todos/", response_model=ToDoResponse, status_code=201)
def create_todo(todo: ToDoCreate, db: Session = Depends(get_db)):
    new_todo = ToDo(**todo.model_dump())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


@app.get("/todos/", response_model=List[ToDoResponse])
def list_todos(db: Session = Depends(get_db)):
    return db.query(ToDo).all()


@app.patch("/todos/{todo_id}", response_model=ToDoResponse)
def update_todo(todo_id: int, todo_update: ToDoUpdate, db: Session = Depends(get_db)):
    todo = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if todo_update.title is not None:
        todo.title = todo_update.title
    if todo_update.completed is not None:
        todo.completed = todo_update.completed
    
    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(todo)
    db.commit()
    return None