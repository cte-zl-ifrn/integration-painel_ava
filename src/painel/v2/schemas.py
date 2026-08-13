from typing import Any, List, Optional

from ninja import Schema


class TokenPairInput(Schema):
    username: str
    password: str


class TokenPairOutput(Schema):
    username: str
    refresh: str
    access: str


class TokenRefreshInput(Schema):
    refresh: str


class TokenRefreshOutput(Schema):
    refresh: str
    access: str


class TokenVerifyInput(Schema):
    token: str


class TokenVerifyOutput(Schema):
    refresh: str
    access: str


class TokenRevokeInput(Schema):
    token: str


class RevokeServiceItem(Schema):
    service_name: str
    url: str
    revoked: bool
    duration: str


class TokenRevokeOutput(Schema):
    detail: str
    revoke_list: List[RevokeServiceItem]


class UserPreferenceSchema(Schema):
    zoom: Optional[str] = "100%"
    configuracao: Optional[str] = "Padrão"


class RoomTypeSchema(Schema):
    slug: str
    rotulo_curto: str
    rotulo_longo: str
    dica: str
    icon: str
    ordem: int
    selecionado: bool
    ativo: bool
    subtitulo: Optional[str] = None


class RoomTypeDetailSchema(RoomTypeSchema):
    quantidade_salas: Optional[int] = None
    suprimir: Optional[str] = None
    filtros: Optional[List[Any]] = None
    ordenacao: Optional[Any] = None


class RoomQuantitiesSchema(Schema):
    inicio: int = 0
    diario: int = 0
    coordenacao: int = 0
    laboratorio: int = 0
    autoinscricoes: int = 0
    backup: int = 0


class FavoritePatchInput(Schema):
    favorite: bool


class FavoritePatchOutput(Schema):
    favorite: bool


class VisiblePatchInput(Schema):
    visible: bool


class VisiblePatchOutput(Schema):
    visible: bool


class NotificationPatchInput(Schema):
    is_read: bool


class ConversationPatchInput(Schema):
    is_read: bool
