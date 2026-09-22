from pydantic_settings import BaseSettings,SettingsConfigDict

class Setting(BaseSettings):
    DEEPSEEK_API : str = None

    model_config = SettingsConfigDict(
        env_file=".env"
    )

config = Setting()