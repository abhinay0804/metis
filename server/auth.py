import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Header, HTTPException
from jose import JWTError, jwt
import bcrypt
from pydantic import BaseModel, EmailStr

from server.config import settings


# --- Data Models ---

@dataclass
class User:
    uid: str
    email: str | None


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class TokenPayload(BaseModel):
    sub: str
    exp: int
    type: str


# --- Password Utilities ---

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


def validate_password(password: str) -> bool:
    """Validate password: min 8 chars, at least 1 uppercase, at least 1 digit."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


# --- Token Utilities ---

def create_access_token(user_id: str, email: str) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": user_id,
        "email": email,
        "exp": int(expire.timestamp()),
        "type": "access"
    }
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": user_id,
        "exp": int(expire.timestamp()),
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenPayload(**payload)
    except JWTError:
        raise HTTPException(
            status_code=401, 
            detail="Could not validate credentials"
        )


# --- FastAPI Dependencies ---

def get_current_user(authorization: str = Header(None)) -> User:
    # Dev bypass for local testing
    if os.environ.get('ALLOW_DEV_BYPASS') == '1' and not authorization:
        return User(uid='dev-user', email='dev@local')
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.split(" ", 1)[1]
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if token_data.type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
            
        return User(
            uid=token_data.sub, 
            email=payload.get("email")
        )
    except JWTError:
        raise HTTPException(
            status_code=401, 
            detail="Could not validate credentials"
        )


# Alias for backward compatibility if existing routes import verify_id_token
verify_id_token = get_current_user
