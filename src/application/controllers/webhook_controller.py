from fastapi import HTTPException
from datetime import datetime
from uuid import uuid4
from typing import cast

from src.domain.messages import MessageType, WhatsAppMessage
from src.domain.services import MessageRouter

class WebhookController:
    def __init__(self, message_router: MessageRouter):
        self.message_router = message_router

    async def handle_webhook(self, data: dict[str, str]) -> dict[str, str]:
        try:
            # Converte o payload do webhook para nosso formato interno
            message = self.convert_webhook_to_message(data)
            message = cast(WhatsAppMessage, message)
            
            # Processa a mensagem e envia respostas
            await self.message_router.handle_incoming_message(message)
            
            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def convert_webhook_to_message(self, data: dict[str, str]) -> WhatsAppMessage | None:
        """
        Converte o payload do webhook do WhatsApp para nosso formato interno
        Esta é uma implementação simplificada - você precisará adaptá-la ao formato real do webhook
        """
        # Implementar conversão do formato do webhook para WhatsAppMessage
        # Exemplo simplificado:
        if "messages" in data:
            message_data = data["messages"][0]

            return WhatsAppMessage(
                message_id=uuid4(),
                sender_id=message_data["from"],  # pyright: ignore[reportArgumentType]
                recipient_id=message_data["to"],  # pyright: ignore[reportArgumentType]
                content=message_data["text"]["body"],  # pyright: ignore[reportArgumentType]
                message_type=MessageType.TEXT,
                timestamp=datetime.now()
            )

        return None