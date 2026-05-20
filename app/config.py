from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str = ""

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"

    meta_app_secret: str = ""
    meta_verify_token: str = ""
    meta_page_access_token: str = ""
    meta_ig_user_id: str = ""

    operator_password: str = ""
    jwt_secret: str = ""

    tax_rate: float = 0.08
    default_currency: str = "USD"

    public_base_url: str = "http://localhost:8000"
    allowed_origins: str = "http://localhost:5173"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


settings = Settings()
