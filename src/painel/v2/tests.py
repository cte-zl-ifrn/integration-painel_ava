import json
import threading
import time

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, override_settings

from mocks.moodle_server import run_moodle_mock_server
from mocks.suap_server import run_suap_mock_server
from painel.v2.brokers import SuapBroker


@pytest.fixture(scope="module", autouse=True)
def mock_servers():
    suap_thread = threading.Thread(target=run_suap_mock_server, kwargs={"host": "127.0.0.1", "port": 8901}, daemon=True)
    moodle_thread = threading.Thread(
        target=run_moodle_mock_server, kwargs={"host": "127.0.0.1", "port": 8902}, daemon=True
    )
    suap_thread.start()
    moodle_thread.start()
    time.sleep(0.5)
    yield


@pytest.mark.django_db
@override_settings(
    SUAP={"BASE_URL": "http://127.0.0.1:8901"},
    JWT_SECRET="test-secret-key-12345",
)
def test_apiv2_token_pair(client: Client):
    response = client.post(
        "/api/v2/token/pair/",
        data=json.dumps({"username": "20261001", "password": "password"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "20261001"
    assert "access" in data
    assert "refresh" in data

    # Test invalid inputs
    resp_invalid = client.post(
        "/api/v2/token/pair/", data=json.dumps({"username": "", "password": ""}), content_type="application/json"
    )
    assert resp_invalid.status_code == 400

    # Test auth failure
    resp_fail = client.post(
        "/api/v2/token/pair/",
        data=json.dumps({"username": "wronguser", "password": "wrongpassword"}),
        content_type="application/json",
    )
    assert resp_fail.status_code == 401


@pytest.mark.django_db
@override_settings(JWT_SECRET="test-secret-key-12345")
def test_apiv2_token_refresh_and_verify_and_revoke(client: Client):
    suap_broker = SuapBroker()
    pair = suap_broker.generate_pair("20261001")

    # Verify
    resp_verify = client.post(
        "/api/v2/token/verify/", data=json.dumps({"token": pair["access"]}), content_type="application/json"
    )
    assert resp_verify.status_code == 200

    resp_verify_invalid = client.post(
        "/api/v2/token/verify/", data=json.dumps({"token": ""}), content_type="application/json"
    )
    assert resp_verify_invalid.status_code == 400

    resp_verify_expired = client.post(
        "/api/v2/token/verify/", data=json.dumps({"token": "invalid.jwt.token"}), content_type="application/json"
    )
    assert resp_verify_expired.status_code == 401

    # Refresh
    resp_refresh = client.post(
        "/api/v2/token/refresh/", data=json.dumps({"refresh": pair["refresh"]}), content_type="application/json"
    )
    assert resp_refresh.status_code == 200

    resp_refresh_invalid = client.post(
        "/api/v2/token/refresh/", data=json.dumps({"refresh": ""}), content_type="application/json"
    )
    assert resp_refresh_invalid.status_code == 400

    resp_refresh_expired = client.post(
        "/api/v2/token/refresh/", data=json.dumps({"refresh": "invalid.jwt.token"}), content_type="application/json"
    )
    assert resp_refresh_expired.status_code == 401

    # Revoke
    resp_revoke = client.post(
        "/api/v2/token/revoke/", data=json.dumps({"token": pair["access"]}), content_type="application/json"
    )
    assert resp_revoke.status_code == 200
    assert resp_revoke.json()["detail"] == "Token revoked"

    resp_revoke_invalid = client.post(
        "/api/v2/token/revoke/", data=json.dumps({"token": ""}), content_type="application/json"
    )
    assert resp_revoke_invalid.status_code == 400

    resp_revoke_expired = client.post(
        "/api/v2/token/revoke/", data=json.dumps({"token": "invalid.jwt.token"}), content_type="application/json"
    )
    assert resp_revoke_expired.status_code == 401


@pytest.mark.django_db
@override_settings(JWT_SECRET="test-secret-key-12345")
def test_apiv2_usuario_info_and_preferencia(client: Client):
    User = get_user_model()
    user = User.objects.create_user(username="testuser", password="password", first_name="Test", last_name="User")
    client.force_login(user)

    # Info
    resp_info = client.get("/api/v2/usuario/info/")
    assert resp_info.status_code == 200
    assert resp_info.json()["matricula"] == "testuser"

    # Preferencia GET
    resp_pref_get = client.get("/api/v2/usuario/preferencia/")
    assert resp_pref_get.status_code == 200

    # Preferencia PATCH
    resp_pref_patch = client.patch(
        "/api/v2/usuario/preferencia/", data=json.dumps({"zoom": "120%"}), content_type="application/json"
    )
    assert resp_pref_patch.status_code == 200
    assert resp_pref_patch.json()["zoom"] == "120%"


@pytest.mark.django_db
def test_apiv2_salas_endpoints(client: Client):
    # GET tipo list
    resp_tipos = client.get("/api/v2/sala/tipo/")
    assert resp_tipos.status_code == 200
    assert len(resp_tipos.json()) >= 6

    # GET quantidades
    resp_qtd = client.get("/api/v2/sala/tipo/quantidades/")
    assert resp_qtd.status_code == 200
    assert "diario" in resp_qtd.json()

    # GET tipo detail
    resp_diario_detail = client.get("/api/v2/sala/tipo/diario/")
    assert resp_diario_detail.status_code == 200
    assert resp_diario_detail.json()["slug"] == "diario"

    # GET tipo ava
    resp_tipo_ava = client.get("/api/v2/sala/tipo/diario/academico/")
    assert resp_tipo_ava.status_code == 200

    # GET progresso
    resp_prog = client.get("/api/v2/sala/progresso/academico/101,102/")
    assert resp_prog.status_code == 200
    assert len(resp_prog.json()) == 2

    # PATCH favorito
    resp_fav = client.patch(
        "/api/v2/sala/favorito/academico/101/", data=json.dumps({"favorite": True}), content_type="application/json"
    )
    assert resp_fav.status_code == 200
    assert resp_fav.json()["favorite"] is True

    # PATCH visivel
    resp_vis = client.patch(
        "/api/v2/sala/visivel/academico/101/", data=json.dumps({"visible": False}), content_type="application/json"
    )
    assert resp_vis.status_code == 200
    assert resp_vis.json()["visible"] is False


@pytest.mark.django_db
def test_apiv2_notificacao_endpoints(client: Client):
    resp_sumario = client.get("/api/v2/notificacao/")
    assert resp_sumario.status_code == 200

    resp_by_ava = client.get("/api/v2/notificacao/academico/")
    assert resp_by_ava.status_code == 200

    resp_by_ids = client.get("/api/v2/notificacao/academico/101/")
    assert resp_by_ids.status_code == 200

    resp_patch = client.patch(
        "/api/v2/notificacao/academico/101/", data=json.dumps({"is_read": True}), content_type="application/json"
    )
    assert resp_patch.status_code == 200


@pytest.mark.django_db
def test_apiv2_conversa_endpoints(client: Client):
    resp_sumario = client.get("/api/v2/conversa/")
    assert resp_sumario.status_code == 200

    resp_by_ava = client.get("/api/v2/conversa/academico/")
    assert resp_by_ava.status_code == 200

    resp_by_ids = client.get("/api/v2/conversa/academico/201/")
    assert resp_by_ids.status_code == 200

    resp_patch = client.patch(
        "/api/v2/conversa/academico/201/", data=json.dumps({"is_read": True}), content_type="application/json"
    )
    assert resp_patch.status_code == 200


@pytest.mark.django_db
@override_settings(SUAP={"BASE_URL": "http://127.0.0.1:8901"})
def test_suap_broker_mock():
    broker = SuapBroker()
    broker.login(None, "20261001", "password")
    assert broker.get_token() == "suap-access-token-for-20261001"
    assert broker.get_user_data()["matricula"] == "20261001"
