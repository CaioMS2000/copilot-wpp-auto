from typing import override, TypedDict
import aiohttp
import asyncio
import logging

from src.domain.interfaces.messaging import MessageSender
from src.domain.messages import WhatsAppMessage, MessageType
from .config import WhatsAppConfig
from .exceptions import WhatsAppAPIError

logger = logging.getLogger(__name__)

class WhatsAppButton(TypedDict):
    id: str
    title: str


class WhatsAppMessageSender(MessageSender):
    config: WhatsAppConfig
    max_retries: int
    retry_delay: float

    def __init__(self, config: WhatsAppConfig, max_retries: int = 3, retry_delay: float = 1.0):
        self.config = config
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session: aiohttp.ClientSession | None = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self._get_headers())
        return self
    
    # async def __aexit__(self, exc_type, exc_val, exc_tb):
    async def __aexit__(self):
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json"
        }
    
    @override
    async def send_message(self, message: WhatsAppMessage) -> bool:
        """
        Envia uma mensagem via WhatsApp Cloud API.
        Retorna True se enviado com sucesso, False caso contrário.
        """
        if not self.session:
            raise RuntimeError("WhatsAppMessageSender must be used as a context manager")
        
        payload = self._create_payload(message)
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.post(self.config.api_url, json=payload) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        logger.info(
                            "Message sent successfully",
                            extra={
                                "message_id": str(message.message_id),
                                "recipient": message.recipient_id,
                                "type": message.message_type.value
                            }
                        )
                        return True
                    
                    error_message = response_data.get("error", {}).get("message", "Unknown error")
                    logger.error(
                        f"Failed to send message: {error_message}",
                        extra={
                            "message_id": str(message.message_id),
                            "status_code": response.status,
                            "attempt": attempt + 1
                        }
                    )
                    
                    if not self._should_retry(response.status):
                        raise WhatsAppAPIError(error_message, response.status)
                    
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    
            except aiohttp.ClientError as e:
                logger.error(
                    f"Network error while sending message: {str(e)}",
                    extra={"message_id": str(message.message_id), "attempt": attempt + 1}
                )
                if attempt == self.max_retries - 1:
                    raise WhatsAppAPIError(f"Network error: {str(e)}")
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        return False
    
    def _create_payload(self, message: WhatsAppMessage) -> dict[str, object]:
        base_payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": message.recipient_id,
        }
        
        if message.message_type == MessageType.TEXT:
            return {
                **base_payload,
                "type": "text",
                "text": {"body": message.content}
            }
        
        elif message.message_type == MessageType.BUTTON_RESPONSE:
            buttons = message.metadata.get("buttons", [])
            buttons_list: list[WhatsAppButton] = []

            if isinstance(buttons, list):
                buttons_list= buttons
                
            return {
                **base_payload,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": message.content},
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {
                                    "id": btn["id"],
                                    "title": btn["title"]
                                }
                            }
                            for btn in buttons_list
                        ]
                    }
                }
            }
        
        return {
                **base_payload,
                "type": "text",
                "text": {"body": "Desculpe, algo deu errado"}
            }
    
    def _should_retry(self, status_code: int) -> bool:
        """Determina se deve tentar reenviar a mensagem baseado no status code"""
        return status_code in {
            408,  # Request Timeout
            429,  # Too Many Requests
            500,  # Internal Server Error
            502,  # Bad Gateway
            503,  # Service Unavailable
            504   # Gateway Timeout
        }