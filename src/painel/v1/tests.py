from unittest.mock import patch

import psycopg
import psycopg_pool
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import DisallowedHost, SuspiciousOperation
from django.http import HttpResponse
from django.test import RequestFactory

from painel.middleware import ExceptionMiddleware
from painel.models import Ambiente


def test_exception_middleware_handles_allowed_exceptions(rf: RequestFactory):
    request = rf.get("/")

    def get_response(req):
        return HttpResponse("OK")

    middleware = ExceptionMiddleware(get_response)
    response = middleware(request)
    assert response.status_code == 200
    assert response.content == b"OK"


def test_exception_middleware_handles_db_timeout(rf: RequestFactory):
    request = rf.get("/")

    def get_response(req):
        raise psycopg_pool.PoolTimeout("Timeout")

    middleware = ExceptionMiddleware(get_response)
    response = middleware(request)
    assert response.status_code == 200
    assert response.content == "Erro de conexão com o banco!".encode("utf-8")


def test_exception_middleware_handles_db_error(rf: RequestFactory):
    request = rf.get("/")

    def get_response(req):
        raise psycopg.errors.Error("DB Error")

    middleware = ExceptionMiddleware(get_response)
    response = middleware(request)
    assert response.status_code == 200
    assert response.content == "Erro de conexão com o banco!".encode("utf-8")


def test_exception_middleware_re_raises_suspicious_operation(rf: RequestFactory):
    request = rf.get("/")

    def get_response(req):
        raise SuspiciousOperation("Suspicious")

    middleware = ExceptionMiddleware(get_response)
    with pytest.raises(SuspiciousOperation):
        middleware(request)


def test_exception_middleware_handles_disallowed_host(rf: RequestFactory):
    request = rf.get("/")

    def get_response(req):
        raise DisallowedHost("Invalid Host")

    middleware = ExceptionMiddleware(get_response)
    response = middleware(request)
    assert response.status_code == 400
    assert "Host Não Permitido (Disallowed Host)".encode("utf-8") in response.content


@pytest.mark.django_db
def test_dashboard_sets_csrf_cookie(client):
    User = get_user_model()
    user = User.objects.create_user(username="testuser", password="password")
    client.force_login(user)

    response = client.get("/")
    assert response.status_code == 200
    assert "csrftoken" in client.cookies


@pytest.mark.django_db
@patch("painel.views.get_json_api")
def test_curso_detalhes_sets_csrf_cookie(mock_get_json_api, client):
    ambiente = Ambiente.objects.create(
        nome="Moodle de Teste",
        url="http://moodle-teste.ifrn.edu.br",
        token="token123",
        cor_mestra="#ffffff",
    )
    mock_get_json_api.return_value = {
        "fullname": "Curso Teste",
        "summary": "Descrição",
        "is_enrolled": False,
        "docentes": [],
        "carga_horaria": "40h",
    }
    response = client.get(f"/curso/{ambiente.id}/123/")
    assert response.status_code == 200
    assert "csrftoken" in client.cookies


@pytest.mark.django_db
@patch("painel.v1.services.get_json")
def test_get_json_api_catches_http_exception(mock_get_json):
    from http.client import HTTPException

    mock_get_json.side_effect = HTTPException("502 - Bad Gateway")

    ambiente = Ambiente.objects.create(
        nome="Moodle de Teste",
        url="http://moodle-teste.ifrn.edu.br",
        token="token123",
        cor_mestra="#ffffff",
    )

    from painel.v1.services import get_json_api

    result = get_json_api(ambiente, "enrol_course", courseid=123, username="testuser")
    assert result is None


@pytest.mark.django_db
@patch("painel.views.get_json_api")
def test_enrol_course_handles_api_http_exception(mock_get_json_api, client):
    User = get_user_model()
    user = User.objects.create_user(username="testuser", password="password", first_name="Test", last_name="User")
    client.force_login(user)

    ambiente = Ambiente.objects.create(
        nome="Moodle de Teste",
        url="http://moodle-teste.ifrn.edu.br",
        token="token123",
        cor_mestra="#ffffff",
    )

    mock_get_json_api.return_value = None

    response = client.post(f"/curso/{ambiente.id}/123/enrol/")
    assert response.status_code == 500
    assert response.json() == {"status": "error", "message": "Falha de comunicação com o AVA."}


def test_api_docs_returns_200(client):
    response = client.get("/api/v1/docs")
    assert response.status_code in [200, 428]


def test_api_openapi_json_returns_200(client):
    response = client.get("/api/v1/openapi.json")
    assert response.status_code in [200, 428]
