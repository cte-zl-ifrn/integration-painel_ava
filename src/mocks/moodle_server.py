import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)

MOCK_NOTIFICATION_SUMMARY = [
    {"ava": "academico", "unreadcount": 2},
    {"ava": "presencial", "unreadcount": 0},
    {"ava": "projetos", "unreadcount": 1},
]

MOCK_CONVERSATION_SUMMARY = [
    {"ava": "academico", "unreadcount": 1, "favourites": 1},
    {"ava": "presencial", "unreadcount": 0, "favourites": 0},
]

MOCK_NOTIFICATIONS = [
    {
        "id": 101,
        "useridfrom": 2,
        "useridto": 1,
        "subject": "Nova tarefa postada",
        "shortenedsubject": "Nova tarefa",
        "text": "Você tem uma nova tarefa no diário de Programação.",
        "fullmessage": "Você tem uma nova tarefa no diário de Programação.",
        "fullmessageformat": 4,
        "fullmessagehtml": "<p>Você tem uma nova tarefa no diário de Programação.</p>",
        "smallmessage": "Nova tarefa",
        "contexturl": "https://moodle.ifrn.edu.br/mod/assign/view.php?id=1",
        "contexturlname": "Ver tarefa",
        "timecreated": "2026-08-13T10:00:00Z",
        "timecreatedpretty": "há 1 hora",
        "timeread": None,
        "read": False,
        "deleted": False,
        "iconurl": "https://moodle.ifrn.edu.br/theme/image.php/boost/assign/1/icon",
        "component": "mod_assign",
        "eventtype": "assign_notification",
        "customdata": None,
    }
]

MOCK_CONVERSATIONS = [
    {
        "id": 201,
        "name": "Grupo de Projetos Integradores",
        "subname": None,
        "imageurl": None,
        "type": 3,
        "membercount": 4,
        "ismuted": False,
        "isfavourite": True,
        "isread": False,
        "unreadcount": 1,
        "members": [
            {
                "id": 3,
                "fullname": "Maria Oliveira",
                "profileurl": "https://moodle.ifrn.edu.br/user/profile.php?id=3",
                "profileimageurl": "https://moodle.ifrn.edu.br/user/pix.php/3/f1.jpg",
                "profileimageurlsmall": "https://moodle.ifrn.edu.br/user/pix.php/3/f2.jpg",
                "isonline": True,
                "showonlinestatus": True,
                "isblocked": False,
                "iscontact": True,
                "isdeleted": False,
                "canmessageevenifblocked": None,
                "canmessage": True,
                "requirescontact": None,
                "cancreatecontact": True,
                "contactrequests": [],
            }
        ],
        "messages": [
            {
                "id": 501,
                "useridfrom": 3,
                "text": "Olá! Conseguiu revisar o relatório de práticas?",
                "timecreated": 1700000000,
            }
        ],
        "candeletemessagesforallusers": True,
    }
]


class MoodleMockRequestHandler(BaseHTTPRequestHandler):
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

        if "favorito" in parsed.path:
            fav = payload.get("favorite", True)
            return self._send_json(200, {"favorite": fav})

        elif "visivel" in parsed.path:
            vis = payload.get("visible", True)
            return self._send_json(200, {"visible": vis})

        elif "notificacao" in parsed.path:
            payload.get("is_read", True)
            return self._send_json(
                200,
                [{"error": False, "data": {"notificationid": 101, "warnings": []}}],
            )

        elif "conversa" in parsed.path:
            payload.get("is_read", True)
            return self._send_json(200, [{"error": False, "data": None}])

        elif "revoke" in parsed.path or "token_revoke" in parsed.path:
            return self._send_json(
                200,
                {
                    "detail": "Token revoked",
                    "revoke_list": [
                        {
                            "service_name": "Moodle Academico",
                            "url": "http://moodle-academico.ifrn.edu.br",
                            "revoked": True,
                            "duration": "PT0.5S",
                        }
                    ],
                },
            )

        elif "refresh" in parsed.path or "token_refresh" in parsed.path:
            return self._send_json(
                200,
                {
                    "refresh": "moodle-refreshed-refresh-token",
                    "access": "moodle-refreshed-access-token",
                },
            )

        self._send_json(200, {"status": "ok"})

    def do_PATCH(self):
        self.do_POST()

    def do_GET(self):
        parsed = urlparse(self.path)
        parse_qs(parsed.query)

        if "notificacao" in parsed.path:
            if parsed.path.strip("/").endswith("notificacao"):
                return self._send_json(200, MOCK_NOTIFICATION_SUMMARY)
            return self._send_json(
                200,
                {
                    "result": MOCK_NOTIFICATIONS,
                    "unreadcount": 1,
                },
            )

        elif "conversa" in parsed.path:
            if parsed.path.strip("/").endswith("conversa"):
                return self._send_json(200, MOCK_CONVERSATION_SUMMARY)
            return self._send_json(200, MOCK_CONVERSATIONS)

        elif "get_atualizacoes_counts" in parsed.path or "get_atualizacoes_counts" in parsed.query:
            return self._send_json(
                200,
                {
                    "unread_conversations_count": 1,
                    "unread_popup_notification_count": 2,
                },
            )

        elif "get_diarios" in parsed.path or "get_diarios" in parsed.query:
            return self._send_json(
                200,
                {
                    "semestres": [{"label": "2026.1", "value": "2026.1"}],
                    "disciplinas": [{"label": "Programação Web", "value": "1"}],
                    "cursos": [{"label": "Técnico em Informática", "value": "1"}],
                    "ambientes": [
                        {
                            "label": "Acadêmico",
                            "value": "academico",
                            "cor": "#0d6efd",
                            "icone": "fa-solid fa-door-open",
                        }
                    ],
                    "diarios": [],
                    "autoinscricoes": [],
                    "reutilizaveis": [],
                },
            )

        elif "get_progresso" in parsed.path or "get_progresso" in parsed.query:
            return self._send_json(
                200,
                [
                    {
                        "id": "20261.1.0028.ZL.1E.POS.0364#123",
                        "progress": 75,
                        "hasprogress": True,
                    }
                ],
            )

        elif "get_course_info" in parsed.path or "get_course_info" in parsed.query:
            return self._send_json(
                200,
                {
                    "fullname": "Curso de Teste Moodle",
                    "summary": "Descrição do curso de teste",
                    "is_enrolled": True,
                    "docentes": ["Prof. Teste"],
                    "carga_horaria": "60h",
                },
            )

        self._send_json(200, [])

    def log_message(self, format, *args):
        pass


def run_moodle_mock_server(host: str = "0.0.0.0", port: int = 8002):  # noqa: S104
    server = ThreadingHTTPServer((host, port), MoodleMockRequestHandler)
    print(f"Servidor Mock do Moodle rodando em http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
