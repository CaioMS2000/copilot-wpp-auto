from abc import ABC, abstractmethod

from src.domain.messages import WhatsAppMessage

class MessageSender(ABC):
    @abstractmethod
    async def send_message(self, message: WhatsAppMessage) -> bool:
        """
        Envia uma mensagem via WhatsApp.
        Retorna True se enviado com sucesso, False caso contrário.
        """
        pass