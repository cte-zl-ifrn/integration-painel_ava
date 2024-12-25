from import_export.resources import ModelResource
from .models import Usuario


class UsuarioResource(ModelResource):
    class Meta:
        model = Usuario
        export_order = (
            "username",
            "nome_registro",
            "nome_usual",
            "nome_social",
            "email",
            "email_secundario",
            "email_google_classroom",
            "email_academico",
            "tipo_usuario",
            "is_superuser",
            "is_active",
            "is_staff",
            "foto",
            "last_json",
        )
        import_id_fields = ("username",)
        fields = export_order
        skip_unchanged = True
