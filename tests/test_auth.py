import pytest
import psycopg2
import hashlib

def get_valid_login_credentials(db_conn_hn):
    """
    Tìm tài khoản và mật khẩu hợp lệ từ site_hn.
    Nếu mật khẩu mã hóa là SHA-256 của '123456' hoặc 'Password123'.
    """
    with db_conn_hn.cursor() as cur:
        cur.execute("SELECT TenDangNhap, MatKhauHash FROM NguoiDungDangNhap LIMIT 5;")
        users = cur.fetchall()
        for username, p_hash in users:
            if p_hash == hashlib.sha256(b"123456").hexdigest():
                return username, "123456"
            elif p_hash == hashlib.sha256(b"Password123").hexdigest():
                return username, "Password123"
    return "giap_gd", "123456"

def test_login_success(client, db_conn_hn):
    """Kiểm tra đăng nhập thành công với tài khoản hợp lệ."""
    username, password = get_valid_login_credentials(db_conn_hn)
    
    response = client.post("/api/auth/login", json={
        "username": username,
        "password": password
    })
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data.get("success") is True
    assert "data" in data
    res_data = data["data"]
    assert "access_token" in res_data
    assert res_data.get("token_type") == "bearer"
    
    user = res_data.get("user")
    assert user is not None
    assert user.get("username") == username
    assert "role_name" in user
    assert "scope" in user

def test_login_invalid_password(client):
    """Kiểm tra đăng nhập với mật khẩu sai -> 401 INVALID_CREDENTIALS."""
    response = client.post("/api/auth/login", json={
        "username": "giap_gd",
        "password": "WrongPassword999"
    })
    
    assert response.status_code == 401
    data = response.json()
    assert data.get("success") is False
    assert "error" in data
    assert data["error"].get("code") == "INVALID_CREDENTIALS"

def test_login_nonexistent_user(client):
    """Kiểm tra đăng nhập với tài khoản không tồn tại -> 401 INVALID_CREDENTIALS."""
    response = client.post("/api/auth/login", json={
        "username": "non_existent_user_xyz",
        "password": "Password123"
    })
    
    assert response.status_code == 401
    data = response.json()
    assert data.get("success") is False
    assert data["error"].get("code") == "INVALID_CREDENTIALS"

def test_get_me_success(client, db_conn_hn):
    """Kiểm tra GET /api/auth/me với Bearer token hợp lệ."""
    username, password = get_valid_login_credentials(db_conn_hn)
    
    login_res = client.post("/api/auth/login", json={
        "username": username,
        "password": password
    })
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]
    
    response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    user = data["data"]
    assert user.get("username") == username

def test_get_me_unauthorized(client):
    """Kiểm tra GET /api/auth/me khi không truyền token hoặc token rác -> 401."""
    # Không header
    res_no_token = client.get("/api/auth/me")
    assert res_no_token.status_code == 401
    
    # Token rác
    res_bad_token = client.get("/api/auth/me", headers={
        "Authorization": "Bearer invalid.jwt.token"
    })
    assert res_bad_token.status_code == 401
