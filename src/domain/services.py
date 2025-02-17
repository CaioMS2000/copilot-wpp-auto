from datetime import datetime
from uuid import uuid4

from .interfaces.messaging import MessageSender
from .entities import CustomerStatus
from .messages import WhatsAppMessage
from .repositories import CustomerRepository, AgentRepository

class MessageRouter:
    customer_repo: CustomerRepository
    agent_repo: AgentRepository
    message_sender: MessageSender

    def __init__(self, customer_repo: CustomerRepository, agent_repo: AgentRepository, message_sender: MessageSender):
        self.customer_repo = customer_repo
        self.agent_repo = agent_repo
        self.message_sender = message_sender
    
    async def route_message(self, message: WhatsAppMessage) -> list[WhatsAppMessage]:
        """
        Rota as mensagens entre cliente, sistema e agente.
        Retorna uma lista de mensagens que precisam ser enviadas como resposta.
        """
        if message.sender_id.startswith("AGENT_"):
            return await self._handle_agent_message(message)
        else:
            return await self._handle_customer_message(message)
    
    async def _handle_customer_message(self, message: WhatsAppMessage) -> list[WhatsAppMessage]:
        customer = await self.customer_repo.get(message.sender_id)
        
        if not customer:
            # Novo cliente
            return self._send_welcome_menu(message.sender_id)
        
        if customer.status == CustomerStatus.WAITING:
            return [WhatsAppMessage.create_system_message(
                message.sender_id,
                "Você está na fila de espera. Em breve um agente irá atendê-lo."
            )]
        
        if customer.status == CustomerStatus.IN_SERVICE:
            # Encaminha mensagem para o agente atual
            return [WhatsAppMessage(
                message_id=uuid4(),
                sender_id=message.sender_id,
                recipient_id=customer.current_agent_id if customer.current_agent_id is not None else "",
                content=f"CLIENTE {message.sender_id}: {message.content}",
                message_type=message.message_type,
                timestamp=datetime.now()
            )]        
        return []
    
    async def _handle_agent_message(self, message: WhatsAppMessage) -> list[WhatsAppMessage]:
        # Extrai o ID do agente da mensagem
        agent_id = message.sender_id
        
        # Verifica comandos especiais do agente
        if message.content.startswith("/"):
            return await self._handle_agent_command(agent_id, message.content)
            
        # Caso contrário, encaminha a mensagem para o cliente atual
        agent = await self.agent_repo.get_by_id(agent_id)  # <-- Correção aqui
        
        if not agent or not agent.current_customer_id:
            return [WhatsAppMessage.create_system_message(
                agent_id,
                "Você não está atendendo nenhum cliente no momento."
            )]
            
        return [WhatsAppMessage(
            message_id=uuid4(),
            sender_id=agent_id,
            recipient_id=agent.current_customer_id,
            content=message.content,
            message_type=message.message_type,
            timestamp=datetime.now()
        )]
    
    def _send_welcome_menu(self, customer_id: str) -> list[WhatsAppMessage]:
        menu_content = """
        Bem-vindo ao nosso atendimento! 
        Por favor, escolha um departamento:
        
        1. Vendas
        2. Suporte
        3. Financeiro
        """
        return [WhatsAppMessage.create_system_message(customer_id, menu_content)]
    
    async def _handle_agent_command(self, agent_id: str, command: str) -> list[WhatsAppMessage]:
        """
        Processa comandos especiais dos agentes:
        /fila - Mostra quantidade de clientes na fila
        /proximo - Pega próximo cliente da fila
        /encerrar - Encerra atendimento atual
        """
        command = command.lower()
        if command == "/fila":
            # Implementar lógica para mostrar fila
            pass
        elif command == "/proximo":
            # Implementar lógica para pegar próximo cliente
            pass
        elif command == "/encerrar":
            # Implementar lógica para encerrar atendimento
            pass
        
        return [WhatsAppMessage.create_system_message(
            agent_id,
            "Comando processado com sucesso."
        )]
    
    async def handle_incoming_message(self, message: WhatsAppMessage) -> None:
        """
        Processa uma mensagem recebida e envia as respostas apropriadas
        """
        response_messages = await self.route_message(message)
        
        # Envia cada mensagem de resposta
        for response in response_messages:
            success = await self.message_sender.send_message(response)
            if not success:
                # Aqui você pode implementar retry logic ou logging
                print(f"Falha ao enviar mensagem para {response.recipient_id}")