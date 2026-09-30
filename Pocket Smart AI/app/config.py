from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    secret_key: str = "change-this-secret-key"

    database_url: str = "sqlite:///./data/pocketsmart.db"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    access_token_expire_minutes: int = 120
    max_upload_mb: int = 5

    allowed_origins: str = (
        "http://127.0.0.1:8000,http://localhost:8000"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]


settings = Settings()