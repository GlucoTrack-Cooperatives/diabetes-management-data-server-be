from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    db_url: str
    dexcom_region: str = "OUS"
    sqs_queue_url: str
    aws_region: str
    env: str = "local"

    # Google Cloud Pub/Sub settings
    gcp_project_id: str = "local-project"
    pubsub_topic: str = "glucose-alerts"
    pubsub_emulator_host: str = None  # Set to "localhost:8085" for local emulator

    model_config = SettingsConfigDict(
        env_file="config/.env.local",  # point to your file
        env_file_encoding="utf-8"
    )

settings = Settings()

# Set Pub/Sub emulator host for local development
if settings.pubsub_emulator_host:
    os.environ['PUBSUB_EMULATOR_HOST'] = settings.pubsub_emulator_host
