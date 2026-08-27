from django.contrib.admin import register, site
from django.contrib.auth.models import Group

from base.admin import BaseModelAdmin

from .models import Grupo

site.unregister(Group)


@register(Grupo)
class GrupoAdmin(BaseModelAdmin):
    pass
