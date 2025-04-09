# services/task-service/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings # Import settings from config.py

# Create async engine instance
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True, # Log SQL queries (useful for debugging)
    future=True # Use SQLAlchemy 2.0 style execution
)

# Create sessionmaker
# expire_on_commit=False prevents attributes from expiring after commit
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() # Commit changes if everything went well
        except Exception:
            await session.rollback() # Rollback on error
            raise
        finally:
            await session.close() # Close session

# We might need Base for Alembic later, but don't need it directly here
# from .models import Base