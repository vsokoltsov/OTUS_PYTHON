import os
import jwt

from app.utils import get_environment_variable

JWT_SECRET = get_environment_variable('JWT_SECRET')
ALGORITHM = 'HS256'


def encode(id):
    """Encode user's id as jwt string."""

    return jwt.encode({'id': id}, JWT_SECRET, algorithm=ALGORITHM)


def decode(hash_string):
    """Decode jwt string value to the dictionary."""

    return jwt.decode(hash_string, JWT_SECRET, algorithms=[ALGORITHM])


def encode_user(user):
    """Decode user information."""

    return encode(user.id)
