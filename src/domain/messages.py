from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    BUTTON_RESPONSE = "button_response"


@dataclass
class WhatsAppMessage:
    message_id: UUID
    sender_id: str
    recipient_id: str
    content: str
    message_type: MessageType
    timestamp: datetime
    metadata: dict[str, object] = {}
    
    @staticmethod
    def create_system_message(recipient_id: str, content: str) -> 'WhatsAppMessage':
        return WhatsAppMessage(
            message_id=uuid4(),
            sender_id="SYSTEM",
            recipient_id=recipient_id,
            content=content,
            message_type=MessageType.TEXT,
            timestamp=datetime.now()
        )
    