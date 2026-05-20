import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "codes" / "Backend"))

import app as app_module


def make_client(tmp_path):
    test_app = app_module.create_app(
        {
            "TESTING": True,
            "CSRF_ENABLED": False,
            "DB_ENGINE": "sqlite",
            "DATABASE": str(tmp_path / "test_forensic.db"),
            "BACKUP_FOLDER": str(tmp_path / "backups"),
            "SECRET_KEY": "test-secret",
        }
    )
    return test_app, test_app.test_client()


def login(client, username="admin", password="admin123"):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


def test_dashboard_and_seed_data_render(tmp_path):
    _, client = make_client(tmp_path)
    response = login(client)
    assert response.status_code == 200
    assert b"Department Dashboard" in response.data

    cases = client.get("/records/cases")
    assert cases.status_code == 200
    assert b"CL-2026-001" in cases.data
    assert b"PM-2026-001" in cases.data


def test_role_based_access_blocks_non_admin_users(tmp_path):
    _, client = make_client(tmp_path)
    login(client, "lab", "lab123")

    assert client.get("/records/evidence").status_code == 200
    assert client.get("/records/lab-tests").status_code == 200
    assert client.get("/users").status_code == 403
    assert client.get("/backup").status_code == 403


def test_patient_create_and_search(tmp_path):
    _, client = make_client(tmp_path)
    login(client)

    response = client.post(
        "/records/patients/new",
        data={
            "patient_no": "PAT-TEST-001",
            "full_name": "Test Patient",
            "nic": "TESTNIC",
            "dob": "2000-01-01",
            "age": "26",
            "gender": "Other",
            "address": "Test address",
            "contact_no": "0700000000",
            "guardian_name": "",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    search = client.get("/records/patients?q=PAT-TEST-001")
    assert search.status_code == 200
    assert b"Test Patient" in search.data
