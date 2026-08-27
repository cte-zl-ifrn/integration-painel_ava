import json
import logging

from django.db import migrations

logger = logging.getLogger(__name__)


def migrate_a4_usuario_to_auth_user(apps, schema_editor):
    try:
        Usuario = apps.get_model("a4", "Usuario")
    except LookupError:
        return

    User = apps.get_model("auth", "User")
    Perfil = apps.get_model("django_suap_auth_profile", "Perfil")
    DadosBrutos = apps.get_model("django_suap_auth_profile", "DadosBrutos")
    Vinculo = apps.get_model("django_suap_auth_profile", "Vinculo")

    for u in Usuario.objects.all():
        user, created = User.objects.get_or_create(
            username=u.username,
            defaults={
                "first_name": u.first_name or "",
                "last_name": u.last_name or "",
                "email": u.email or "",
                "is_staff": u.is_staff,
                "is_active": u.is_active,
                "is_superuser": u.is_superuser,
                "last_login": u.last_login,
                "date_joined": u.date_joined,
                "password": u.password or "",
            },
        )

        perfil, _ = Perfil.objects.get_or_create(
            user=user,
            defaults={
                "settings": u.settings or {},
                "first_login": u.first_login,
                "nome_registro": u.nome_registro or u.nome or "",
                "nome_social": u.nome_social or "",
                "nome_usual": u.nome_usual or "",
                "email_secundario": u.email_secundario or "",
                "email_google_classroom": u.email_google_classroom or "",
                "email_academico": u.email_academico or "",
                "email_preferencial": u.email or "",
                "url_foto_150x200": u.foto or "",
                "tipo_usuario": u.tipo_usuario or "",
            },
        )

        if u.last_json:
            try:
                data_dict = json.loads(u.last_json)
                if isinstance(data_dict, dict):
                    DadosBrutos.objects.update_or_create(perfil=perfil, defaults={"data": data_dict})
            except Exception as exc:
                logger.warning("Falha ao migrar last_json do usuario %s: %s", u.username, exc)

        if u.vinculos and isinstance(u.vinculos, dict):
            meus_vinculos = u.vinculos.get("results") or u.vinculos.get("meus_vinculos") or []
            if isinstance(meus_vinculos, list):
                for item in meus_vinculos:
                    if isinstance(item, dict):
                        det = item.get("detalhamento") if isinstance(item.get("detalhamento"), dict) else {}
                        Vinculo.objects.get_or_create(
                            perfil=perfil,
                            identificador=str(item.get("identificador", "")),
                            defaults={
                                "tipo": item.get("tipo", ""),
                                "campus": item.get("campus") or det.get("campus"),
                                "cargo": item.get("cargo") or det.get("cargo"),
                                "categoria": item.get("categoria") or det.get("categoria"),
                                "modalidade": item.get("modalidade") or det.get("modalidade"),
                                "nivel_ensino": item.get("nivel_ensino") or det.get("nivel_ensino"),
                                "curso": item.get("curso") or det.get("curso"),
                                "ativo": item.get("ativo") if item.get("ativo") is not None else det.get("ativo"),
                                "detalhamento": det,
                                "estrangeiro": bool(item.get("estrangeiro", False)),
                            },
                        )


def reverse_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("a4", "0012_alter_historicalusuario_tipo_usuario_and_more"),
        ("django_suap_auth_profile", "0001_initial"),
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_a4_usuario_to_auth_user, reverse_code=reverse_migration),
    ]
