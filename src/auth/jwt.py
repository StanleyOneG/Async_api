from jose import jwt
from datetime import datetime
from fastapi import Request
import logging
from functools import wraps
from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from core.config import JWT_PUBLIC_KEY as public_key

logger = logging.getLogger(__name__)


def check_permission(user_permissions, endpoint_permission):
    if endpoint_permission in user_permissions:
        return True
    return False


def check_auth(endpoint_permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs['request']
            token = request.cookies.get('access_token_cookie')
            if not token:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED, detail='Token is missing'
                )
            decoded_token = jwt.decode(token, public_key, algorithms=['RS256'])
            if decoded_token['exp'] > datetime.now().timestamp():
                permissions = decoded_token['permissions']
                if check_permission(permissions, endpoint_permission):
                    value = await func(*args, **kwargs)
                    return value
                else:
                    raise HTTPException(
                        status_code=HTTPStatus.UNAUTHORIZED, detail='You have no permission'
                    )
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail='Token expired'
            )

        return wrapper

    return decorator
