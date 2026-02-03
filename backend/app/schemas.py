from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# ============ User Schemas ============
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ TodoList Schemas ============
class TodoListBase(BaseModel):
    name: str

class TodoListCreate(TodoListBase):
    pass

class TodoListResponse(TodoListBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ TodoItem Schemas ============
class TodoItemBase(BaseModel):
    title: str
    completed: bool = False

class TodoItemCreate(TodoItemBase):
    pass

class TodoItemUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None

class TodoItemResponse(TodoItemBase):
    id: int
    list_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Extended Responses (with relationships) ============
class TodoListWithItems(TodoListResponse):
    items: List[TodoItemResponse] = []

class UserWithLists(UserResponse):
    todo_lists: List[TodoListResponse] = []


# ============ Old Todo Schemas (keep for backward compatibility) ============
class ToDoBase(BaseModel):
    title: str
    completed: bool = False

class ToDoCreate(ToDoBase):
    pass

class ToDoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None

class ToDoResponse(ToDoBase):
    id: int
    
    class Config:
        from_attributes = True