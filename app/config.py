from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Autonomous Multi-Agent Travel Planner API"
    VERSION: str = "1.0.0"

    OPENAI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    SERPAPI_KEY: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"
    RAPIDAPI_KEY: str = ""
    MAPBOX_ACCESS_TOKEN: str = ""
    FOURSQUARE_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()


def get_settings() -> Settings:
    return settings