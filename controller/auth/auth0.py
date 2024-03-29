from functools import wraps
from jose import jwt
from flask import request
import requests
from flask import _request_ctx_stack
import logging


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


class Auth0:
    def __init__(self, setting):
        self.logger = logging.getLogger("Auth0")
        self.auth0_domain = setting.AUTH_DOMAIN
        self.api_audience = setting.API_AUDIENCE
        self.algorithms = setting.ALGORITHMS

    def get_token_auth_header(self):
        """Obtains the Access Token from the Authorization Header
        """
        auth = request.headers.get("Authorization", None)
        if not auth:
            raise AuthError(
                {
                    "code": "authorization_header_missing",
                    "description": "Authorization header is expected",
                },
                401,
            )

        parts = auth.split()

        if parts[0].lower() != "bearer":
            raise AuthError(
                {
                    "code": "invalid_header",
                    "description": "Authorization header must start with" " Bearer",
                },
                401,
            )
        elif len(parts) == 1:
            raise AuthError(
                {"code": "invalid_header", "description": "Token not found"}, 401
            )
        elif len(parts) > 2:
            raise AuthError(
                {
                    "code": "invalid_header",
                    "description": "Authorization header must be" " Bearer token",
                },
                401,
            )

        token = parts[1]
        return token

    def requires_auth(self, f):
        """Determines if the Access Token is valid
        """

        @wraps(f)
        def decorated(*args, **kwargs):
            token = self.get_token_auth_header()
            jsonurl = requests.get(
                "https://" + self.auth0_domain + "/.well-known/jwks.json"
            )
            if jsonurl.status_code != 200:
                raise AuthError(
                    {
                        "code": "invalid_response",
                        "description": "response code is invalid",
                    },
                    401,
                )

            jwks = jsonurl.json()

            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"],
                    }

            if not rsa_key:
                raise AuthError(
                    {
                        "code": "invalid_header",
                        "description": "Unable to find appropriate key",
                    },
                    401,
                )

            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=self.algorithms,
                    audience=self.api_audience,
                    issuer="https://" + self.auth0_domain + "/",
                )
            except jwt.ExpiredSignatureError:
                raise AuthError(
                    {"code": "token_expired", "description": "token is expired"}, 401
                )
            except jwt.JWTClaimsError:
                raise AuthError(
                    {
                        "code": "invalid_claims",
                        "description": "incorrect claims,"
                        "please check the audience and issuer",
                    },
                    401,
                )
            except Exception:
                raise AuthError(
                    {
                        "code": "invalid_header",
                        "description": "Unable to parse authentication" " token.",
                    },
                    401,
                )

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)

        return decorated
