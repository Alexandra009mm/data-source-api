from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Configuración del bucket donde guardaremos los datos crudos
    s3_bucket: str

    # Región donde se encuentra el bucket
    aws_default_region: str = "us-east-2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
