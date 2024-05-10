from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "NetEase Music Scrobbler"
    maloja_api_url: str
    maloja_api_token: str
    api_key: str

    model_config = SettingsConfigDict(env_file=".env")
