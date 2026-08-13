import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

MOCK_USERS = {
    "20261001": {
        "username": "20261001",
        "nome": "Aluno Teste da Silva",
        "email": "aluno.teste@escolar.ifrn.edu.br",
        "tipo_vinculo": "Aluno",
        "url_foto_150x200": "https://suap.ifrn.edu.br/media/fotos/150x200/aluno.jpg",
        "nome_usual": "Aluno Teste",
        "cpf": "000.000.000-00",
        "rg": "0000000 SSP/RN",
        "matricula": "20261001",
        "tipo_usuario": "Aluno (Técnico Integrado)",
        "vinculo": {
            "turno": "Matutino",
            "campus_curso": "ZL: 123456 - Informática",
            "campus": "ZL",
            "curso": "123456 - Informática",
            "matriz": "001 - Informática",
            "ingresso": "2026/1",
            "ira": "85,50",
            "categoria": "aluno",
            "situacao": "Matriculado",
            "situacao_sistemica": "Formando",
            "matricula_regular": True,
        },
        "vinculos": [
            {
                "detalhamento": {
                    "modalidade": "Presencial",
                    "nivel_ensino": "Técnico",
                    "ativo": True,
                    "cargo": "",
                    "categoria": "Aluno",
                },
                "estrangeiro": False,
            }
        ],
    },
    "1234567": {
        "username": "1234567",
        "nome": "Professor Servidor da Silva",
        "email": "servidor.teste@ifrn.edu.br",
        "tipo_vinculo": "Servidor",
        "url_foto_150x200": "https://suap.ifrn.edu.br/media/fotos/150x200/servidor.jpg",
        "nome_usual": "Professor Servidor",
        "cpf": "111.111.111-11",
        "rg": "1111111 SSP/RN",
        "matricula": "1234567",
        "tipo_usuario": "Servidor (Docente)",
        "vinculo": {
            "cargo": "Professor do Ensino Básico, Técnico e Tecnológico",
            "campus": "CNAT",
            "categoria": "docente",
            "situacao": "Ativo Permanente",
            "situacao_sistemica": "Ativo",
            "matricula_regular": True,
        },
        "vinculos": [
            {
                "detalhamento": {
                    "modalidade": "Presencial",
                    "nivel_ensino": "Superior",
                    "ativo": True,
                    "cargo": "Professor",
                    "categoria": "Servidor",
                },
                "estrangeiro": False,
            }
        ],
    },
}


class SuapMockRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict or list):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {}

        if parsed.path == "/api/token/pair":
            username = payload.get("username", "")
            password = payload.get("password", "")
            if not username or not password:
                return self._send_json(
                    400,
                    {
                        "detail": "Invalid input.",
                        "code": "invalid",
                        "username": "username is required",
                        "password": "password is required",
                    },
                )
            if username in MOCK_USERS or password == "password":  # noqa: S105
                return self._send_json(
                    200,
                    {
                        "username": username,
                        "access": f"suap-access-token-for-{username}",
                        "refresh": f"suap-refresh-token-for-{username}",
                    },
                )
            return self._send_json(
                401,
                {
                    "detail": "No active account found with the given credentials",
                    "code": "authentication_failed",
                },
            )

        elif parsed.path == "/api/token/refresh":
            refresh = payload.get("refresh", "")
            if not refresh:
                return self._send_json(400, {"detail": "Invalid input.", "code": "invalid"})
            return self._send_json(
                200,
                {
                    "access": "suap-access-token-refreshed",
                    "refresh": "suap-refresh-token-refreshed",
                },
            )

        elif parsed.path == "/api/token/verify":
            token = payload.get("token", "")
            if not token:
                return self._send_json(400, {"detail": "Invalid input.", "code": "invalid"})
            return self._send_json(200, {"token": token, "valid": True})

        self._send_json(404, {"detail": "Not found"})

    def do_GET(self):
        parsed = urlparse(self.path)
        auth_header = self.headers.get("Authorization", "")

        username = "20261001"
        if "for-" in auth_header:
            username = auth_header.split("for-")[-1]

        user_data = MOCK_USERS.get(username, MOCK_USERS["20261001"])

        if parsed.path == "/api/rh/meus-dados/":
            return self._send_json(200, user_data)
        elif parsed.path == "/api/rh/meus-vinculos/":
            return self._send_json(200, user_data.get("vinculos", []))
        elif parsed.path == "/api/ensino/meus-dados-aluno/":
            return self._send_json(200, user_data)
        elif parsed.path == "/api/ensino/meus-diarios/":
            return self._send_json(200, [])

        self._send_json(404, {"detail": "Not found"})

    def log_message(self, format, *args):
        pass


def run_suap_mock_server(host: str = "0.0.0.0", port: int = 8001):  # noqa: S104
    server = ThreadingHTTPServer((host, port), SuapMockRequestHandler)
    print(f"Servidor Mock do SUAP rodando em http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
