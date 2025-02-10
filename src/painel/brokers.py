from django.utils.translation import gettext as _
import http
import logging
import json
import hashlib
from django.utils.timezone import now
from django.http import HttpRequest
from django.core.exceptions import ValidationError
from django.contrib import auth
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from a4.models import Usuario
from cryptography.fernet import Fernet
from painel.constants import CRYPTOGRAPHY_KEY, JWT_SECRET
import jwt
import datetime
from datetime import timezone
import requests

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
        try:
            response = requests.get(
                f"{settings.SUAP['BASE_URL']}/api/v2/minhas-informacoes/meus-dados/",
                headers={"Authorization": f"Bearer {self.__access_token}"},
                timeout=2,
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Response: {result}")
        except requests.RequestException as e:
            logger.error(f"Erro ao tentar acessar dados do usuário. {type(e)}:{e}")
        self.__data = result


    def __suap_user_token(self, username: str, password: str):
        try:
            response = requests.post(
                f"{settings.SUAP['BASE_URL']}/api/token/pair",
                json={"username": username, "password": password},
                timeout=2,
            )
            response.raise_for_status()
            self.__access_token = response.json()["access"]
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro ao tentar obter token do SUAP. {type(e)}:{e}")
            if e.response is not None and e.response.status_code == 401:
                raise ValidationError(_("Usuário ou senha inválidos"), code="401") # Corrected line
            else:
                raise Exception(f"Erro ao obter token do SUAP: {e}") from e
        except requests.RequestException as e:
            logger.error(f"Erro ao tentar obter token do SUAP. {type(e)}:{e}")
            raise Exception(f"Erro de requisição ao SUAP: {e}") from e
        


    def login(self, request: HttpRequest, username: str, password: str) -> None:
        try:
            self.__suap_user_token(username, password)
        except http.client.HTTPException as e:
            if e.status == 401:
                raise ValidationError(_("Usuário ou senha inválidos"), code="401")
            logger.warning(f"Erro {e.status} ao tentar autenticar no SUAP. {type(e)}:{e}")
            return
        try:
            self.__suap_user_data()
        except Exception as e:
            logger.error(f"Erro ao tentar acessar dados do usuário. {type(e)}:{e}")
            raise ValidationError(_("Erro ao tentar acessar dados do usuário"), code="401")

        nome_completo = self.__data.get("nome", "")
        nome_split = nome_completo.split()
        first_name = nome_split[0] if nome_split else ""
        last_name = nome_split[-1] if len(nome_split) > 1 else ""

        user_data_mapping = {
            "username": self.__data.get("matricula"),
            "email": self.__data.get("email"),
            "foto": self.__data.get("url_foto_150x200"),
            "first_name": first_name,
            "last_name": last_name,
            "nome_registro": nome_completo,
            "nome_usual": self.__data.get("nome_usual"),
            "tipo_usuario": self.__data.get("tipo_vinculo"),
        }
        
        try:
            user, created = Usuario.objects.update_or_create(
                username=user_data_mapping["username"],
                defaults=user_data_mapping
            )
        except Exception as e:
            print('e', e)
            return


class TokenBroker:
    def __init__(self) -> None:
        self.__token_jwt = None

    def generate(self, username: str, expiration_days: int) -> str:
        expiration = datetime.datetime.now(timezone.utc).timestamp() + expiration_days * 24 * 60 * 60
        self.__token_jwt = jwt.encode(
            {"username": username, "exp": expiration},
            JWT_SECRET,
            algorithm="HS256",
        )
        return self.__token_jwt

    def verify(self, token: str) -> str:
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])["username"]
        except jwt.ExpiredSignatureError:
            return ''
        except jwt.InvalidTokenError:
            logger.error(f"Token inválido: {token}")
            return ''
        except Exception as e:
            logger.error(f"Erro ao tentar validar token. {type(e)}:{e}")
            return ''