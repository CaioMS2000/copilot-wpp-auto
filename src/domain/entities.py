from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Department(Enum):
    SALES = "sales"
    SUPPORT = "support"
    BILLING = "billing"


class CustomerStatus(Enum):
    WAITING = "waiting"
    IN_SERVICE = "in_service"
    FINISHED = "finished"


@dataclass
class Customer:
    customer_id: str
    department: Department | None
    status: CustomerStatus
    current_agent_id: str | None = None
    waiting_since: datetime | None = None


@dataclass
class Agent:
    agent_id: str
    department: Department
    is_available: bool = True
    current_customer_id: str | None = None
