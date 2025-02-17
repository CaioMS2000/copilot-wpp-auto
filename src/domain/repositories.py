from abc import ABC, abstractmethod

from .entities import Agent, Customer, Department


class CustomerRepository(ABC):
    @abstractmethod
    async def add(self, customer: Customer) -> None:
        pass
    
    @abstractmethod
    async def get(self, customer_id: str) -> Customer | None:
        pass
    
    @abstractmethod
    async def update(self, customer: Customer) -> None:
        pass

class AgentRepository(ABC):
    @abstractmethod
    async def get_available_agent(self, department: Department) -> Agent | None:
        pass
    
    @abstractmethod
    async def update_agent_status(self, agent_id: str, is_available: bool, current_customer_id: str | None = None) -> None:
        pass
    
    @abstractmethod
    async def get_by_id(self, agent_id: str) -> Agent | None:
        pass