"""Central configuration via pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Local / SQLAlchemy database settings (dev mirror of Catalyst Data Store)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(
        default="postgresql+psycopg2://cip:cip_dev_password@localhost:5432/crime_intelligence",
        alias="DATABASE_URL",
    )
    pool_size: int = Field(default=5, alias="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=10, alias="DATABASE_MAX_OVERFLOW")


class CatalystSettings(BaseSettings):
    """Zoho Catalyst service configuration.

    Production MUST use Catalyst services per catalyst.txt.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    project_id: str = Field(default="", alias="CATALYST_PROJECT_ID")
    zaid: str = Field(default="", alias="CATALYST_ZAID")
    env: str = Field(default="Development", alias="CATALYST_ENV")
    org_id: str = Field(default="", alias="CATALYST_ORG_ID")
    project_domain: str = Field(
        default="https://api.catalyst.zoho.com",
        alias="CATALYST_PROJECT_DOMAIN",
    )
    # SDK init: auto | function (initialize) | third_party (initialize_app)
    # See https://docs.catalyst.zoho.com/en/sdk/python/v1/setup/
    init_mode: Literal["auto", "function", "third_party"] = Field(
        default="auto",
        alias="CATALYST_INIT_MODE",
    )
    sdk_scope: Literal["admin", "user"] = Field(
        default="admin",
        alias="CATALYST_SDK_SCOPE",
    )

    # Functions / AppSail
    function_name: str = Field(default="", alias="CATALYST_FUNCTION_NAME")
    function_id: str = Field(default="", alias="CATALYST_FUNCTION_ID")
    function_url: str = Field(default="", alias="CATALYST_FUNCTION_URL")
    appsail_app_name: str = Field(default="", alias="CATALYST_APPSAIL_APP_NAME")
    appsail_url: str = Field(default="", alias="CATALYST_APPSAIL_URL")

    # Hosting / domain
    client_hosting_url: str = Field(default="", alias="CATALYST_CLIENT_HOSTING_URL")
    domain: str = Field(default="", alias="CATALYST_DOMAIN")

    # Data plane
    datastore_endpoint: str = Field(default="", alias="CATALYST_DATASTORE_ENDPOINT")
    datastore_table_prefix: str = Field(
        default="cip_", alias="CATALYST_DATASTORE_TABLE_PREFIX"
    )
    datastore_mock: bool = Field(default=False, alias="CATALYST_DATASTORE_MOCK")
    datastore_mock_path: str = Field(
        default=".data/catalyst_datastore.json",
        alias="CATALYST_DATASTORE_MOCK_PATH",
    )
    # Optional: prefer Table ID from console over name (under table name in Data Store)
    table_case_master: str = Field(default="", alias="CATALYST_TABLE_CASE_MASTER")
    table_victim: str = Field(default="", alias="CATALYST_TABLE_VICTIM")
    table_accused: str = Field(default="", alias="CATALYST_TABLE_ACCUSED")
    table_act_section: str = Field(default="", alias="CATALYST_TABLE_ACT_SECTION")
    nosql_table: str = Field(default="", alias="CATALYST_NOSQL_TABLE")
    nosql_endpoint: str = Field(default="", alias="CATALYST_NOSQL_ENDPOINT")
    stratus_bucket: str = Field(default="", alias="CATALYST_STRATUS_BUCKET")
    stratus_endpoint: str = Field(default="", alias="CATALYST_STRATUS_ENDPOINT")
    cache_segment: str = Field(default="", alias="CATALYST_CACHE_SEGMENT")
    cache_endpoint: str = Field(default="", alias="CATALYST_CACHE_ENDPOINT")

    # AI / ML
    quickml_endpoint: str = Field(default="", alias="CATALYST_QUICKML_ENDPOINT")
    quickml_model_id: str = Field(default="", alias="CATALYST_QUICKML_MODEL_ID")
    rag_knowledge_base_id: str = Field(
        default="", alias="CATALYST_RAG_KNOWLEDGE_BASE_ID"
    )
    rag_endpoint: str = Field(default="", alias="CATALYST_RAG_ENDPOINT")
    zia_automl_endpoint: str = Field(default="", alias="CATALYST_ZIA_AUTOML_ENDPOINT")
    zia_endpoint: str = Field(default="", alias="CATALYST_ZIA_ENDPOINT")
    smartbrowz_endpoint: str = Field(default="", alias="CATALYST_SMARTBROWZ_ENDPOINT")

    # Auth / gateway (Self Client for third-party SDK)
    auth_domain: str = Field(default="", alias="CATALYST_AUTH_DOMAIN")
    client_id: str = Field(default="", alias="CATALYST_CLIENT_ID")
    client_secret: str = Field(default="", alias="CATALYST_CLIENT_SECRET")
    refresh_token: str = Field(default="", alias="CATALYST_REFRESH_TOKEN")
    api_gateway_url: str = Field(default="", alias="CATALYST_API_GATEWAY_URL")
    api_key: str = Field(default="", alias="CATALYST_API_KEY")

    # Events / orchestration
    signals_topic: str = Field(default="", alias="CATALYST_SIGNALS_TOPIC")
    circuits_id: str = Field(default="", alias="CATALYST_CIRCUITS_ID")
    cron_job_id: str = Field(default="", alias="CATALYST_CRON_JOB_ID")


class Settings(BaseSettings):
    """Root application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = Field(default="crime-intelligence-platform", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_dir: str = Field(default="logs", alias="LOG_DIR")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    # postgres = local/CI SQLAlchemy; catalyst = Cloud Scale Data Store (or mock)
    persistence_backend: Literal["postgres", "catalyst"] = Field(
        default="postgres",
        alias="PERSISTENCE_BACKEND",
    )

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    catalyst: CatalystSettings = Field(default_factory=CatalystSettings)


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton for FastAPI dependency injection."""
    return Settings()
