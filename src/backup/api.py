from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from ninja import Router

from backup.models import ArquivoBackup

router = Router()


@router.api_operation(["GET", "OPTIONS"], "/backup/baixar/{arquivo_id}/")
def baixar(request: HttpRequest, arquivo_id: int):
    arquivo = get_object_or_404(
        ArquivoBackup, id=arquivo_id, donoarquivobackup__dono_backup__username=request.user.username
    )
    return HttpResponseRedirect(arquivo.url_sem_dados)
