from painel import get_installed_themes


def create_localhost_themes(apps, schema_editor):
    Theme = apps.get_model('painel', 'Theme')
    for nome, apelido in get_installed_themes():
        try:
            Theme.objects.update_or_create(nome=nome, default=dict(apelido=apelido, active=True))
        except:
            print(f"Erro ao atualizar/criar {nome}")


def create_localhost_contratante(apps, schema_editor):
    Theme = apps.get_model('painel', 'Theme')
    
    Contrante = apps.get_model('painel', 'Contrante')
    contrante = Contrante.objects.create(
        url = "http://painel",
        url_logo = "https://ead.ifrn.edu.br/wp-content/uploads/2020/08/SUAP.png",
        titulo = "Painel AVA",
        nome_contratante = "IFRN",
        observacoes = "",
        rodape = "",
        css_personalizado = "",
        menu_personalizado = "",
        regex_coordenacao = "",
        default_theme = Theme.objects.filter(nome='ifrn25').first(),
        useraway_active = False,
        useraway_account = None,
        vlibras_active = None,
        active = True,
    )
    
    Ambiente = apps.get_model('painel', 'Ambiente')
    Ambiente.objects.create(
        contratante = contrante,
        nome = "local",
        url = "http://moodle",
        token = "changeme",
        cor_mestra = '#2dcfe0',
        active = True
    )

    AddedTheme = apps.get_model('painel', 'AddedTheme')
    for nome, apelido in get_installed_themes():
        AddedTheme.objects.create(
            contratante=contrante,
            theme = Theme.objects.get(nome=nome),
            active = True
        )
