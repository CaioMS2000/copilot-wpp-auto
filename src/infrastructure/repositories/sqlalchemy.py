from typing import override
from sqlalchemy import select
from src.domain.entities import Customer, Agent, Department, CustomerStatus
from src.domain.repositories import CustomerRepository, AgentRepository
from ..database.models import CustomerModel, AgentModel
from ..database.connection import Database

class SQLAlchemyCustomerRepository(CustomerRepository):
    db: Database

    def __init__(self, database: Database):
        self.db = database
    
    @override
    async def add(self, customer: Customer) -> None:
        async with self.db.async_session() as session:
            db_customer = CustomerModel(
                customer_id=customer.customer_id,
                department=customer.department,
                status=customer.status,
                current_agent_id=customer.current_agent_id,
                waiting_since=customer.waiting_since
            )
            session.add(db_customer)
            await session.commit()
    
    @override
    async def get(self, customer_id: str) -> Customer | None:
        async with self.db.async_session() as session:
            result = await session.execute(
                select(CustomerModel).where(CustomerModel.customer_id == customer_id)
            )
            db_customer = result.scalar_one_or_none()
            
            if not db_customer:
                return None
            
            return Customer(
                customer_id=db_customer.customer_id,
                department=db_customer.department,
                status=db_customer.status,
                current_agent_id=db_customer.current_agent_id,
                waiting_since=db_customer.waiting_since
            )
    
    @override
    async def update(self, customer: Customer) -> None:
        async with self.db.async_session() as session:
            result = await session.execute(
                select(CustomerModel).where(CustomerModel.customer_id == customer.customer_id)
            )
            db_customer = result.scalar_one_or_none()
            
            if db_customer:
                db_customer.department = customer.department
                db_customer.status = customer.status
                db_customer.current_agent_id = customer.current_agent_id
                db_customer.waiting_since = customer.waiting_since
                await session.commit()
    
    async def get_waiting_customers(self, department: Department) -> list[Customer]:
        async with self.db.async_session() as session:
            result = await session.execute(
                select(CustomerModel)
                .where(
                    CustomerModel.department == department,
                    CustomerModel.status == CustomerStatus.WAITING
                )
                .order_by(CustomerModel.waiting_since)
            )
            db_customers = result.scalars().all()
            
            return [
                Customer(
                    customer_id=db_customer.customer_id,
                    department=db_customer.department,
                    status=db_customer.status,
                    current_agent_id=db_customer.current_agent_id,
                    waiting_since=db_customer.waiting_since
                )
                for db_customer in db_customers
            ]

class SQLAlchemyAgentRepository(AgentRepository):
    def __init__(self, database: Database):
        self.db = database
    
    @override
    async def get_available_agent(self, department: Department) -> Agent | None:
        async with self.db.async_session() as session:
            result = await session.execute(
                select(AgentModel)
                .where(
                    AgentModel.department == department,
                    AgentModel.is_available == True
                )
                .limit(1)
            )
            db_agent = result.scalar_one_or_none()
            
            if not db_agent:
                return None
            
            return Agent(
                agent_id=db_agent.agent_id,
                department=db_agent.department,
                is_available=db_agent.is_available,
                current_customer_id=db_agent.current_customer_id
            )
    
    @override
    async def get_by_id(self, agent_id: str) -> Agent | None:
        async with self.db.async_session() as session:
            result = await session.execute(
                select(AgentModel).where(AgentModel.agent_id == agent_id)
            )
            db_agent = result.scalar_one_or_none()
            
            if not db_agent:
                return None
            
            return Agent(
                agent_id=db_agent.agent_id,
                department=db_agent.department,
                is_available=db_agent.is_available,
                current_customer_id=db_agent.current_customer_id
            )
    
    @override
    async def update_agent_status(self, agent_id: str, is_available: bool, current_customer_id: str | None = None) -> None:
        async with self.db.async_session() as session:
            result = await session.execute(
                select(AgentModel).where(AgentModel.agent_id == agent_id)
            )
            db_agent = result.scalar_one_or_none()
            
            if db_agent:
                db_agent.is_available = is_available
                db_agent.current_customer_id = current_customer_id
                await session.commit()