import logging
from http import HTTPStatus

import jwt
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from py_auth_header_parser import parse_auth_header
from storage.redis import cache

from core.settings import get_settings

logger = logging.getLogger(__name__)

redis_setting = get_settings().redis_settings


def get_error_json():
    return JSONResponse(
        status_code=HTTPStatus.UNAUTHORIZED,
        content={"Error": "Authorization error"},
    )


def apply_middleware(app: FastAPI):
    @app.middleware("http")
    async def check_jwt(request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header is None:
            return get_error_json()
        is_authenticated = parse_header(auth_header)
        if not is_authenticated:
            return get_error_json()
        return await call_next(request)


@cache.cache()
def parse_header(auth_header) -> bool:
    parsed_auth_header = parse_auth_header(auth_header)
    jwt_token = parsed_auth_header["access_token"]
    username = None
    roles = None
    try:
        decoded_jwt = jwt.decode(
            jwt_token,
            get_settings().app.jwt_public_key,
            algorithms=[get_settings().app.jwt_algorithm],
        )
        username = decoded_jwt["username"]
        roles = decoded_jwt["roles"]
    except (jwt.DecodeError, jwt.ExpiredSignatureError) as jwt_error:
        logger.exception(jwt_error)
    return bool(username and roles)
