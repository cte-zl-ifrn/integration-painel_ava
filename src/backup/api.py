import requests
from ninja import NinjaAPI
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from backup.models import ArquivoBackup


api = NinjaAPI(docs_decorator=staff_member_required, urls_namespace='api')


@api.api_operation(["GET", "OPTIONS"], "/backup/baixar/{arquivo_id}/")
def baixar(request: HttpRequest, arquivo_id: int):
    arquivo = get_object_or_404(ArquivoBackup, id=arquivo_id, donoarquivobackup__dono_backup__username=request.user.username)
    return HttpResponseRedirect(arquivo.url_sem_dados)
