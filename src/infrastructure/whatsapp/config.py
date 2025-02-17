from dataclasses import dataclass

@dataclass
class WhatsAppConfig:
    phone_number_id: str
    access_token: str
    api_version: str = "v18.0"
    base_url: str = "https://graph.facebook.com"

    @property
    def api_url(self) -> str:
        return f"{self.base_url}/{self.api_version}/{self.phone_number_id}/messages"