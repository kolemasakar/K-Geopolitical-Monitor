from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "K-Geopolitical Monitor"
    environment: str = "development"


settings = Settings()
