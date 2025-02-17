from fastapi import FastAPI
from src.infrastructure.database.connection import Database
from src.infrastructure.whatsapp.config import WhatsAppConfig
from src.infrastructure.whatsapp.sender import WhatsAppMessageSender
from src.infrastructure.repositories.sqlalchemy import SQLAlchemyCustomerRepository, SQLAlchemyAgentRepository
from src.domain.services import MessageRouter
from src.application.routes.webhook_routes import create_webhook_router

# Configurações iniciais
config = WhatsAppConfig(
    phone_number_id="your_phone_number_id",
    access_token="your_access_token"
)
message_sender = WhatsAppMessageSender(config)
database = Database("postgresql+asyncpg://user:password@localhost/whatsapp_service")
customer_repo = SQLAlchemyCustomerRepository(database)
agent_repo = SQLAlchemyAgentRepository(database)
router = MessageRouter(
    customer_repo=customer_repo,
    agent_repo=agent_repo,
    message_sender=message_sender
)

# Criação da aplicação FastAPI
app = FastAPI()

# Configuração das rotas
webhook_router = create_webhook_router(router)
app.include_router(webhook_router)