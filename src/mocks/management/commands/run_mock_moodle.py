from django.core.management.base import BaseCommand

from mocks.moodle_server import run_moodle_mock_server


class Command(BaseCommand):
    help = "Inicia o servidor mock standalone do Moodle / tool_painelava"

    def add_arguments(self, parser):
        parser.add_argument("--host", type=str, default="0.0.0.0", help="Host para escutar")  # noqa: S104
        parser.add_argument("--port", type=int, default=8002, help="Porta para escutar")

    def handle(self, *args, **options):
        host = options["host"]
        port = options["port"]
        self.stdout.write(self.style.SUCCESS(f"Iniciando Mock do Moodle em http://{host}:{port}..."))
        run_moodle_mock_server(host=host, port=port)
