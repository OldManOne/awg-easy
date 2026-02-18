from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _reset_peers() -> None:
    response = client.get("/api/peers")
    assert response.status_code == 200
    for peer in response.json():
        delete_response = client.delete(f"/api/peers/{peer['id']}")
        assert delete_response.status_code == 204


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_peer_crud_update_and_config():
    _reset_peers()

    create = client.post(
        "/api/peers",
        json={
            "name": "alice",
            "allowed_ips": "10.8.0.2/32",
            "awg_jc": 4,
            "awg_jmin": 55,
            "awg_jmax": 1200,
            "awg_s1": 30,
            "awg_s2": 90,
        },
    )
    assert create.status_code == 201
    peer = create.json()
    assert peer["name"] == "alice"

    get_response = client.get(f"/api/peers/{peer['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == peer["id"]

    update_response = client.put(
        f"/api/peers/{peer['id']}",
        json={
            "name": "alice-updated",
            "allowed_ips": "10.8.0.4/32",
            "awg_jc": 5,
            "awg_jmin": 60,
            "awg_jmax": 1400,
            "awg_s1": 25,
            "awg_s2": 95,
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "alice-updated"

    config_response = client.get(f"/api/peers/{peer['id']}/config")
    assert config_response.status_code == 200
    config_payload = config_response.json()
    assert "[Interface]" in config_payload["config"]
    assert "Jc = 5" in config_payload["config"]

    delete_response = client.delete(f"/api/peers/{peer['id']}")
    assert delete_response.status_code == 204


def test_peer_validation_and_duplicate_name_errors():
    _reset_peers()

    invalid_ip = client.post(
        "/api/peers",
        json={
            "name": "bad-ip",
            "allowed_ips": "not-an-ip",
            "awg_jc": 4,
            "awg_jmin": 55,
            "awg_jmax": 1200,
            "awg_s1": 30,
            "awg_s2": 90,
        },
    )
    assert invalid_ip.status_code == 422

    first = client.post(
        "/api/peers",
        json={
            "name": "bob",
            "allowed_ips": "10.8.0.5/32",
            "awg_jc": 3,
            "awg_jmin": 50,
            "awg_jmax": 1000,
            "awg_s1": 20,
            "awg_s2": 80,
        },
    )
    assert first.status_code == 201

    second = client.post(
        "/api/peers",
        json={
            "name": "bob",
            "allowed_ips": "10.8.0.6/32",
            "awg_jc": 3,
            "awg_jmin": 50,
            "awg_jmax": 1000,
            "awg_s1": 20,
            "awg_s2": 80,
        },
    )
    assert second.status_code == 409
