from typing import Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database site_hn (Coordinator & HN Shard)
    DB_HN_HOST: str = "localhost"
    DB_HN_PORT: int = 5431
    DB_HN_NAME: str = "qlns_hn"
    DB_HN_USER: str = "postgres"
    DB_HN_PASSWORD: str = "PasswordHN_123"

    # Database site_dn (DN Shard)
    DB_DN_HOST: str = "localhost"
    DB_DN_PORT: int = 5434
    DB_DN_NAME: str = "qlns_dn"
    DB_DN_USER: str = "postgres"
    DB_DN_PASSWORD: str = "PasswordDN_123"

    # Database site_hcm (HCM Shard)
    DB_HCM_HOST: str = "localhost"
    DB_HCM_PORT: int = 5433
    DB_HCM_NAME: str = "qlns_hcm"
    DB_HCM_USER: str = "postgres"
    DB_HCM_PASSWORD: str = "PasswordHCM_123"

    # MinIO S3 Object Storage
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "admin_minio"
    MINIO_SECRET_KEY: str = "PasswordMinio_123"
    MINIO_BUCKET: str = "nhansu-bucket"
    MINIO_SECURE: bool = False

    # JWT Settings
    JWT_SECRET: str = "super_secret_spacex_hrm_jwt_key_2026_!@#$%^"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    def get_db_params(self, site_key: str) -> Dict[str, Any]:
        site_key = site_key.lower()
        if site_key == "site_hn":
            return {
                "host": self.DB_HN_HOST,
                "port": self.DB_HN_PORT,
                "dbname": self.DB_HN_NAME,
                "user": self.DB_HN_USER,
                "password": self.DB_HN_PASSWORD,
                "connect_timeout": 3,
                "options": "-c statement_timeout=5000"
            }
        elif site_key == "site_dn":
            return {
                "host": self.DB_DN_HOST,
                "port": self.DB_DN_PORT,
                "dbname": self.DB_DN_NAME,
                "user": self.DB_DN_USER,
                "password": self.DB_DN_PASSWORD,
                "connect_timeout": 3,
                "options": "-c statement_timeout=5000"
            }
        elif site_key == "site_hcm":
            return {
                "host": self.DB_HCM_HOST,
                "port": self.DB_HCM_PORT,
                "dbname": self.DB_HCM_NAME,
                "user": self.DB_HCM_USER,
                "password": self.DB_HCM_PASSWORD,
                "connect_timeout": 3,
                "options": "-c statement_timeout=5000"
            }
        raise ValueError(f"Unknown database site: {site_key}")


settings = Settings()
