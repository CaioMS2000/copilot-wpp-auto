from datetime import datetime, timezone
from sqlalchemy import Enum, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from src.domain.entities import Department, CustomerStatus

class Base(DeclarativeBase):
    pass

class CustomerModel(Base):
    __tablename__: str = "customers"
    
    customer_id: Mapped[str] = mapped_column(String, primary_key=True)
    department: Mapped[Department | None] = mapped_column(Enum(Department))
    status: Mapped[CustomerStatus] = mapped_column(Enum(CustomerStatus))
    current_agent_id: Mapped[str | None] = mapped_column(String, ForeignKey("agents.agent_id"))
    waiting_since: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_interaction: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    conversation_expiration: Mapped[int] = mapped_column(Integer, default=3600)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )

class AgentModel(Base):
    __tablename__: str = "agents"
    
    agent_id: Mapped[str] = mapped_column(String, primary_key=True)
    department: Mapped[Department] = mapped_column(Enum(Department))
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    current_customer_id: Mapped[str | None] = mapped_column(String, ForeignKey("customers.customer_id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )