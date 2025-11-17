from django.http import HttpRequest


def request2dict(request: HttpRequest):
    {k: v for k, v in request.headers.items()}


def get_installed_themes() -> list[str]:
    from django.apps import apps

    # Percorrer a lista de applications do django e retornar o name de todas que tenham a propriedade is_painel_theme e ela seja igual a True
    themes: list[str] = []
    for app_config in apps.get_app_configs():
        # Checa se o app tem o atributo 'is_painel_theme' e se está habilitado
        if getattr(app_config, 'is_painel_theme', False):
            themes.append((app_config.name.split('_')[1], app_config.verbose_name))
    return themes


def get_added_themes() -> list[str]:
    from django.apps import apps
    from painel.models import Contrante

    # Percorrer a lista de applications do django e retornar o name de todas que tenham a propriedade is_painel_theme e ela seja igual a True
    return Contrante.objects.first().addedtheme_set.all()
