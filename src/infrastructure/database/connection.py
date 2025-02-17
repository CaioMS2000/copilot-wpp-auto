from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from .models import Base


class Database:
    def __init__(self, connection_string: str):
        self.engine = create_async_engine(connection_string)
        self.async_session = async_sessionmaker(
            self.engine, 
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)