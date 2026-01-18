from painel import get_installed_themes


def create_localhost_themes(apps, schema_editor):
    Theme = apps.get_model('painel', 'Theme')
    for nome, apelido in get_installed_themes():
        try:
            Theme.objects.update_or_create(nome=nome, defaults=dict(apelido=apelido, active=True))
        except Exception as e:
            print(f"Erro ao atualizar/criar {nome}. Mensagem: {e}")


def create_localhost_ambiente(apps, schema_editor):
    Ambiente = apps.get_model('painel', 'Ambiente')
    Ambiente.objects.create(
        nome = "local",
        url = "http://moodle",
        token = "changeme",
        cor_mestra = '#2dcfe0',
        active = True
    )
