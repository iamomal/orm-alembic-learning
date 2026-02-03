from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship: one user has many todo lists
    todo_lists = relationship("TodoList", back_populates="owner", cascade="all, delete-orphan")


class TodoList(Base):
    __tablename__ = "todo_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # "Home", "School", etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="todo_lists")
    items = relationship("TodoItem", back_populates="todo_list", cascade="all, delete-orphan")


class TodoItem(Base):
    __tablename__ = "todo_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign key to TodoList
    list_id = Column(Integer, ForeignKey("todo_lists.id"), nullable=False)
    
    # Relationship
    todo_list = relationship("TodoList", back_populates="items")


# Keep the old ToDo model for now (we'll migrate away from it)
class ToDo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)