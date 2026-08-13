import datetime
import http
import logging
from datetime import timezone

import jwt
import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext as _

from a4.models import Usuario

logger = logging.getLogger(__name__)


class SuapBroker:
    def __init__(self) -> None:
        self.__access_token = None
        self.__data = {}

    def get_user_data(self) -> dict:
        return self.__data

    def get_token(self) -> str:
        return self.__access_token

    def __suap_user_data(self):
        result = None
        urls_to_try = [
            f"{settings.SUAP['BASE_URL']}/api/rh/meus-dados/",
            f"{settings.SUAP['BASE_URL']}/api/ensino/meus-dados-aluno/",
            f"{settings.SUAP['BASE_URL']}/api/v2/minhas-informacoes/meus-dados/",
        ]
        for url in urls_to_try:
            try:
                response = requests.get(
                    url,
                    headers={"Authorization": f"Bearer {self.__access_token}"},
                    timeout=getattr(settings, "DEFAULT_HTTP_TIMEOUT", 5),
                )
                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f"Suap user data response from {url}: {result}")
                    break
            except requests.RequestException as e:
                logger.debug(f"Erro ao acessar {url}: {e}")
        self.__data = result or {}

    def __suap_user_token(self, username: str, password: str):
        try:
            response = requests.post(
                f"{settings.SUAP['BASE_URL']}/api/token/pair",
                json={"username": username, "password": password},
                timeout=getattr(settings, "DEFAULT_HTTP_TIMEOUT", 5),
            )
            response.raise_for_status()
            self.__access_token = response.json()["access"]
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro ao tentar obter token do SUAP. {type(e)}:{e}")
            if e.response is not None and e.response.status_code == 401:
                raise ValidationError(_("Usuário ou senha inválidos"), code="401")
            else:
                raise Exception(f"Erro ao obter token do SUAP: {e}") from e
        except requests.RequestException as e:
            logger.error(f"Erro ao tentar obter token do SUAP. {type(e)}:{e}")
            raise Exception(f"Erro de requisição ao SUAP: {e}") from e

    def login(self, request: HttpRequest, username: str, password: str) -> None:
        try:
            self.__suap_user_token(username, password)
        except http.client.HTTPException as e:
            if getattr(e, "status", None) == 401:
                raise ValidationError(_("Usuário ou senha inválidos"), code="401")
            logger.warning(f"Erro ao tentar autenticar no SUAP. {type(e)}:{e}")
            return
        try:
            self.__suap_user_data()
        except Exception as e:
            logger.error(f"Erro ao tentar acessar dados do usuário. {type(e)}:{e}")
            raise ValidationError(_("Erro ao tentar acessar dados do usuário"), code="401")

        if not self.__data:
            raise ValidationError(_("Erro ao tentar acessar dados do usuário"), code="401")

        nome_completo = self.__data.get("nome", "")
        nome_split = nome_completo.split()
        first_name = nome_split[0] if nome_split else ""
        last_name = nome_split[-1] if len(nome_split) > 1 else ""

        username_mapped = self.__data.get("matricula") or self.__data.get("username") or username

        user_data_mapping = {
            "username": username_mapped,
            "email": self.__data.get("email", ""),
            "foto": self.__data.get("url_foto_150x200", ""),
            "first_name": first_name,
            "last_name": last_name,
            "nome_registro": nome_completo,
            "nome_usual": self.__data.get("nome_usual", ""),
            "tipo_usuario": self.__data.get("tipo_vinculo", ""),
        }

        try:
            Usuario.objects.update_or_create(username=user_data_mapping["username"], defaults=user_data_mapping)
        except Exception as e:
            logger.error(f"Erro ao salvar usuário: {e}")
            return


class TokenBroker:
    def __init__(self) -> None:
        self.__token_jwt = None

    def generate(self, username: str, expiration_days: int) -> str:
        expiration = datetime.datetime.now(timezone.utc).timestamp() + expiration_days * 24 * 60 * 60
        jwt_secret = getattr(settings, "JWT_SECRET", "secret")
        self.__token_jwt = jwt.encode(
            {"username": username, "exp": expiration},
            jwt_secret,
            algorithm="HS256",
        )
        return self.__token_jwt

    def verify(self, token: str) -> str:
        try:
            jwt_secret = getattr(settings, "JWT_SECRET", "secret")
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            return payload.get("username", "")
        except jwt.ExpiredSignatureError:
            return ""
        except jwt.InvalidTokenError:
            logger.error(f"Token inválido: {token}")
            return ""
        except Exception as e:
            logger.error(f"Erro ao tentar validar token. {type(e)}:{e}")
            return ""
