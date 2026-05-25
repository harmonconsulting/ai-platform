from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str = "AI Platform"

    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str

    OPENAI_API_KEY: str = ""

    OLLAMA_BASE_URL: str = "http://localhost:11434"

    JWT_SECRET: str = "change-this-dev-secret"

    class Config:
        env_file = ".env"


settings = Settings()
