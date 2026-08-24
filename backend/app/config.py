from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    gemini_api_key: str
    gemini_model: str

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str
    mysql_database: str = "ai_document_assistant"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"


settings = Settings()