import logging
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from django.contrib import auth
from a4.models import Usuario as UsuarioA4
import requests

logger = logging.getLogger(__name__)


class GoToHTTPSMiddleware(MiddlewareMixin):
    """
    Force all requests to use HTTPs when behind a reverse proxy.

    .. note::
        ``settings.GO_TO_HTTPS`` needs to be True.
        The RP need to inform HTTP_X_FORWARDED_PROTO and HTTP_X_FORWARDED_HOST.
        If RP dont inform HTTP_X_FORWARDED_PROTO http will be assumed.
    """

    def process_request(self, request):
        meta = request.META

        if not getattr(settings, "GO_TO_HTTPS", False):
            return None

        host = meta["HTTP_X_FORWARDED_HOST"] or request.get_host()
        url = "https://%s%s" % (host, request.get_full_path())

        if "HTTP_X_FORWARDED_PROTO" in meta and meta["HTTP_X_FORWARDED_PROTO"] == "http":
            return HttpResponseRedirect(url)

        if "HTTP_X_FORWARDED_PROTO" not in meta:
            return HttpResponseRedirect(url)


class AuthMobileUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        dont_have_session = request.session.session_key is None
        is_valid_path = "/painel/api/v1/" in request.path
        is_not_options_method = request.method != "OPTIONS"

        if dont_have_session and is_valid_path and is_not_options_method:
            authorization_header = request.headers.get("Authorization")
            if authorization_header is None:
                request.META["HTTP_AUTHORIZATION"] = "None"
                return self.get_response(request)

            authorization = authorization_header.split(" ")
            if authorization[0] != "Token" or len(authorization) != 2:
                request.META["HTTP_AUTHORIZATION"] = "None"
                return self.get_response(request)

            response = requests.post(
                "http://login/api/v1/verify/",
                json={"token": authorization[1]},
            ).json()

            user = UsuarioA4.objects.filter(username=response["username"]).first()
            if user is not None:
                auth.login(request, user)
                response = self.get_response(request)
                auth.logout(request)
                return response
        else:
            return self.get_response(request)