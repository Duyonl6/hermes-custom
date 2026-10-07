import os
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Môi trường test tách biệt: DB tạm, có seed demo, tắt webhook
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="tnc-test-")
os.environ["AUTO_SEED"] = "1"
os.environ["DEMO_MODE"] = "1"
os.environ["DISCORD_WEBHOOK_URL"] = ""
os.environ["VIETQR_BANK_ID"] = "VCB"
os.environ["VIETQR_ACCOUNT_NO"] = "0123456789"
os.environ["VIETQR_ACCOUNT_NAME"] = "TIEM NHA CAM"

from fastapi.testclient import TestClient  # noqa: E402

from app import db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _app_started():
    with TestClient(app):  # chạy lifespan → init DB + seed
        yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def conn():
    c = db.connect()
    yield c
    c.close()


def csrf_of(html: str) -> str:
    m = re.search(r'name="csrf" value="([^"]+)"', html)
    assert m, "không tìm thấy csrf token trong trang"
    return m.group(1)


def login(client: TestClient, email: str, password: str = "demo1234") -> str:
    token = csrf_of(client.get("/login").text)
    r = client.post("/login", data={"email": email, "password": password, "csrf": token, "next": "/"}, follow_redirects=False)
    assert r.status_code == 303, r.text[:300]
    # token mới sau khi session được làm mới
    return csrf_of(client.get("/account").text)
