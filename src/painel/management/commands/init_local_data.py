# painel/management/commands/init_local_data.py
from django.core.management.base import BaseCommand
from django.conf import settings
from painel.models import Theme, Contrante, Ambiente

class Command(BaseCommand):
    help = "Cadastra temas e contratante padrão para ambiente local"

    def handle(self, *args, **options):

        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("❌ Este comando não pode ser executado em produção!"))
            return
        
        # Criação dos temas
        theme_old, created1 = Theme.objects.get_or_create(
            nome="ifrn23",
            defaults={"active": True},
        )
        theme_padrao, created2 = Theme.objects.get_or_create(
            nome="ifrn25",
            defaults={"active": True},
        )

        # Criação do contratante local
        contratante, created3 = Contrante.objects.get_or_create(
            nome_contratante="IFRN",
            defaults={
                "url": "https://ava.ifrn.edu.br",
                "url_logo": "https://nice-beach-0f5779c10.4.azurestaticapps.net/static/dashboard/img/logo_ifrn_zl.png",
                "titulo": "Painel AVA",
                "observacoes": "",
                "rodape": "",
                "default_theme": theme_padrao,
                "active": True,
            },
        )

        # --- Ambiente ---
        ambiente, created4 = Ambiente.objects.get_or_create(
            nome="Moodle Local",
            defaults={
                "contratante": contratante,
                "url": "http://moodle",
                "token": "changeme",
                "cor_mestra": "#2dcfe0",
                "active": True,
            },
        )

        msgs = []
        if created1:
            msgs.append("✅ Tema atual criado")
        if created2:
            msgs.append("✅ Tema antigo criado")
        if created3:
            msgs.append("✅ Contratante criado")
        if created4:
            msgs.append("✅ Ambiente Local criado")

        if not msgs:
            self.stdout.write(self.style.WARNING("⚠️  Todos os dados já existiam — nada foi criado."))
        else:
            for msg in msgs:
                self.stdout.write(self.style.SUCCESS(msg))
            self.stdout.write(self.style.SUCCESS("\n🎉 Dados locais inicializados com sucesso!"))
