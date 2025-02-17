from fastapi import APIRouter
from src.application.controllers.webhook_controller import WebhookController
from src.domain.services import MessageRouter

def create_webhook_router(message_router: MessageRouter) -> APIRouter:
    """
    Cria e configura o router para o endpoint /webhook.
    """
    router = APIRouter(prefix="/api/v1")  # Prefixo opcional para versionamento da API
    webhook_controller = WebhookController(message_router)

    @router.post("/webhook")
    async def webhook(data: dict[str, str]):
        return await webhook_controller.handle_webhook(data)

    return router