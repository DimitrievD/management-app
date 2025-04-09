# services/task-service/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func # For default timestamps

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False) # Added length limit
    description = Column(Text, nullable=True)
    status = Column(String(50), index=True, default="todo") # e.g., todo, inprogress, done
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # We will link to Keycloak User ID (sub), which is a string (UUID)
    # Store it directly, or create a separate User mapping table if needed
    assignee_id = Column(String, index=True, nullable=True)
    reporter_id = Column(String, index=True, nullable=False) # Who created the task

    # Add relationships later if needed (e.g., to a Project model)
    # project_id = Column(Integer, ForeignKey("projects.id"))
    # project = relationship("Project", back_populates="tasks")

# Example Project model (optional for now)
# class Project(Base):
#     __tablename__ = "projects"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), unique=True, index=True, nullable=False)
#     description = Column(Text, nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#
#     tasks = relationship("Task", back_populates="project")