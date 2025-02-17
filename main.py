from typing import cast
from fastapi import FastAPI, HTTPException
from src.domain.messages import WhatsAppMessage
from src.domain.services import MessageRouter
from src.infrastructure.database.connection import Database
from src.infrastructure.whatsapp.config import WhatsAppConfig
from src.infrastructure.whatsapp.sender import WhatsAppMessageSender
from src.infrastructure.repositories.sqlalchemy import SQLAlchemyCustomerRepository, SQLAlchemyAgentRepository

app = FastAPI()
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

@app.post("/webhook")
async def webhook(data: dict[str, object]):
    try:
        # Converte o payload do webhook para nosso formato interno
        message = convert_webhook_to_message(data)
        message = cast(WhatsAppMessage, message)
        
        # Processa a mensagem e envia respostas
        await router.handle_incoming_message(message)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def convert_webhook_to_message(data: dict[str, object]) -> WhatsAppMessage|None:
    """
    Converte o payload do webhook do WhatsApp para nosso formato interno
    Esta é uma implementação simplificada - você precisará adaptá-la ao formato real do webhook
    """
    # Implementar conversão do formato do webhook para WhatsAppMessage
    pass