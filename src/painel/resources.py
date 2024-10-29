from import_export.resources import ModelResource
from painel.models import Ambiente


class AmbienteResource(ModelResource):
    class Meta:
        model = Ambiente
        export_order = (
            "nome",
            "url",
            "token",
            "cor_mestra",
            "active",
        )
        import_id_fields = ("nome",)
        fields = export_order
        skip_unchanged = True
