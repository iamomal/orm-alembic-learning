from pydantic import BaseModel

class ToDoBase(BaseModel):
    title: str
    completed: bool = False

class ToDoCreate(ToDoBase):
    pass

class ToDoUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None

class ToDoResponse(ToDoBase):
    id: int
    
    class Config:
        from_attributes = True  # Changed from orm_mode