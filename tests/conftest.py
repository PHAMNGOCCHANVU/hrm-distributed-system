import sys
import os
from pathlib import Path
import pytest
import psycopg2
from minio import Minio

# Thêm đường dẫn root dự án và backend vào sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
TESTS_DIR = ROOT_DIR / "tests"

for path in [str(ROOT_DIR), str(BACKEND_DIR), str(TESTS_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Thông số kết nối Database 3 sites
DB_CONFIGS = {
    "site_hn": {
        "host": "localhost",
        "port": 5431,
        "dbname": "qlns_hn",
        "user": "postgres",
        "password": "PasswordHN_123"
    },
    "site_dn": {
        "host": "localhost",
        "port": 5434,
        "dbname": "qlns_dn",
        "user": "postgres",
        "password": "PasswordDN_123"
    },
    "site_hcm": {
        "host": "localhost",
        "port": 5433,
        "dbname": "qlns_hcm",
        "user": "postgres",
        "password": "PasswordHCM_123"
    }
}

# Thông số kết nối MinIO
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "admin_minio"
MINIO_SECRET_KEY = "PasswordMinio_123"
MINIO_BUCKET = "nhansu-bucket"

@pytest.fixture(scope="session")
def minio_client():
    """Khởi tạo MinIO client phục vụ kiểm thử."""
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    return client

@pytest.fixture(scope="session")
def db_conn_hn():
    """Kết nối trực tiếp tới site_hn (Coordinator & Shard HN)."""
    conn = psycopg2.connect(**DB_CONFIGS["site_hn"])
    conn.autocommit = True
    yield conn
    conn.close()

@pytest.fixture(scope="session")
def db_conn_dn():
    """Kết nối trực tiếp tới site_dn (Shard DN)."""
    conn = psycopg2.connect(**DB_CONFIGS["site_dn"])
    conn.autocommit = True
    yield conn
    conn.close()

@pytest.fixture(scope="session")
def db_conn_hcm():
    """Kết nối trực tiếp tới site_hcm (Shard HCM)."""
    conn = psycopg2.connect(**DB_CONFIGS["site_hcm"])
    conn.autocommit = True
    yield conn
    conn.close()

@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient fixture."""
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as test_client:
        yield test_client
