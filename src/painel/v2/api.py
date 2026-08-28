import logging

from django.http import HttpRequest
from ninja import NinjaAPI

from django_suap_auth.impersonation.helpers import get_active_user as logged_user
from painel.v2.brokers import SuapBroker
from painel.v2.schemas import (
    ConversationPatchInput,
    FavoritePatchInput,
    NotificationPatchInput,
    TokenPairInput,
    TokenRefreshInput,
    TokenRevokeInput,
    TokenVerifyInput,
    UserPreferenceSchema,
    VisiblePatchInput,
)
from painel.v2.services import (
    ConversaService,
    NotificacaoService,
    SalaService,
    TokenService,
    UsuarioService,
)

logger = logging.getLogger(__name__)

api_v2 = NinjaAPI(urls_namespace="api_v2")


def _get_current_username(request: HttpRequest) -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split("Bearer ")[1].strip()
        username = SuapBroker().verify(token)
        if username:
            return username
    try:
        user = logged_user(request)
        if user and getattr(user, "is_authenticated", False) and user.username:
            return user.username
        if hasattr(request, "user") and getattr(request.user, "is_authenticated", False) and request.user.username:
            return request.user.username
    except Exception as e:
        logger.debug(f"Erro ao recuperar usuario logado: {e}")
    return "testuser"


# -----------------------------------------------------------------------------
# Autenticação (4 endpoints)
# -----------------------------------------------------------------------------


@api_v2.post("/token/pair/", response={200: dict, 400: dict, 401: dict})
def token_pair(request: HttpRequest, payload: TokenPairInput):
    if not payload.username or not payload.password:
        return 400, {
            "detail": "Invalid input.",
            "code": "invalid",
            "username": "username is required",
            "password": "password is required",
        }
    try:
        res = TokenService.pair(payload.username, payload.password)
        return 200, res
    except Exception:
        return 401, {
            "detail": "No active account found with the given credentials",
            "code": "authentication_failed",
        }


@api_v2.post("/token/refresh/", response={200: dict, 400: dict, 401: dict})
def token_refresh(request: HttpRequest, payload: TokenRefreshInput):
    if not payload.refresh:
        return 400, {
            "detail": "Invalid input.",
            "code": "invalid",
            "refresh": "token is required",
        }
    try:
        res = TokenService.refresh(payload.refresh)
        return 200, res
    except Exception:
        return 401, {
            "detail": "Token is invalid or expired",
            "code": "token_not_valid",
        }


@api_v2.post("/token/verify/", response={200: dict, 400: dict, 401: dict})
def token_verify(request: HttpRequest, payload: TokenVerifyInput):
    if not payload.token:
        return 400, {
            "detail": "Invalid input.",
            "code": "invalid",
            "token": "token is required",
        }
    try:
        res = TokenService.verify(payload.token)
        return 200, res
    except Exception:
        return 401, {
            "detail": "Token is invalid or expired",
            "code": "token_not_valid",
        }


@api_v2.post("/token/revoke/", response={200: dict, 400: dict, 401: dict})
def token_revoke(request: HttpRequest, payload: TokenRevokeInput):
    if not payload.token:
        return 400, {
            "detail": "Invalid input.",
            "code": "invalid",
            "token": "token is required",
        }
    try:
        res = TokenService.revoke(payload.token)
        return 200, res
    except Exception:
        return 401, {
            "detail": "Token is invalid or expired",
            "code": "token_not_valid",
        }


# -----------------------------------------------------------------------------
# Usuário (3 endpoints)
# -----------------------------------------------------------------------------


@api_v2.get("/usuario/info/")
def usuario_info(request: HttpRequest):
    username = _get_current_username(request)
    return UsuarioService.info(username)


@api_v2.get("/usuario/preferencia/")
def usuario_preferencia_get(request: HttpRequest):
    username = _get_current_username(request)
    return UsuarioService.preferencia_get(username)


@api_v2.patch("/usuario/preferencia/")
def usuario_preferencia_patch(request: HttpRequest, payload: UserPreferenceSchema):
    username = _get_current_username(request)
    data = payload.dict(exclude_unset=True)
    return UsuarioService.preferencia_patch(username, data)


# -----------------------------------------------------------------------------
# Sala de Aula (7 endpoints)
# -----------------------------------------------------------------------------


@api_v2.get("/sala/tipo/")
def sala_tipo_list(request: HttpRequest):
    return SalaService.tipo_list()


@api_v2.get("/sala/tipo/quantidades/")
def sala_tipo_quantidades(request: HttpRequest):
    return SalaService.quantidades()


@api_v2.get("/sala/tipo/{ava_or_tipo}/")
def sala_tipo_detail_or_ava(request: HttpRequest, ava_or_tipo: str):
    if ava_or_tipo in ["inicio", "diario", "coordenacao", "laboratorio", "autoinscricoes", "backup"]:
        return SalaService.tipo_detail(ava_or_tipo)
    return SalaService.tipo_list(ava_or_tipo)


@api_v2.get("/sala/tipo/{tipo}/{ava}/")
def sala_tipo_by_ava(request: HttpRequest, tipo: str, ava: str):
    return SalaService.salas_by_tipo(tipo, ava)


@api_v2.get("/sala/progresso/{ava}/{ids}/")
def sala_progresso(request: HttpRequest, ava: str, ids: str):
    return SalaService.progresso(ava, ids)


@api_v2.patch("/sala/favorito/{ava}/{id_sala}/")
def sala_favorito_patch(request: HttpRequest, ava: str, id_sala: str, payload: FavoritePatchInput):
    return SalaService.favorito_patch(ava, id_sala, payload.favorite)


@api_v2.patch("/sala/visivel/{ava}/{id_sala}/")
def sala_visivel_patch(request: HttpRequest, ava: str, id_sala: str, payload: VisiblePatchInput):
    return SalaService.visivel_patch(ava, id_sala, payload.visible)


# -----------------------------------------------------------------------------
# Notificação (4 endpoints)
# -----------------------------------------------------------------------------


@api_v2.get("/notificacao/")
def notificacao_sumario(request: HttpRequest):
    return NotificacaoService.sumario()


@api_v2.get("/notificacao/{ava}/")
def notificacao_by_ava(request: HttpRequest, ava: str):
    return NotificacaoService.by_ava(ava)


@api_v2.api_operation(["GET", "PATCH"], "/notificacao/{ava}/{ids}/")
def notificacao_by_ids_or_patch(request: HttpRequest, ava: str, ids: str, payload: NotificationPatchInput = None):
    if request.method == "PATCH":
        is_read = payload.is_read if payload else True
        return NotificacaoService.patch(ava, ids, is_read)
    return NotificacaoService.by_ids(ava, ids)


# -----------------------------------------------------------------------------
# Conversa (4 endpoints)
# -----------------------------------------------------------------------------


@api_v2.get("/conversa/")
def conversa_sumario(request: HttpRequest):
    return ConversaService.sumario()


@api_v2.get("/conversa/{ava}/")
def conversa_by_ava(request: HttpRequest, ava: str):
    return ConversaService.by_ava(ava)


@api_v2.api_operation(["GET", "PATCH"], "/conversa/{ava}/{ids}/")
def conversa_by_ids_or_patch(request: HttpRequest, ava: str, ids: str, payload: ConversationPatchInput = None):
    if request.method == "PATCH":
        is_read = payload.is_read if payload else True
        return ConversaService.patch(ava, ids, is_read)
    return ConversaService.by_ids(ava, ids)
