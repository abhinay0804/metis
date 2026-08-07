from server.auth import settings
from jose import jwt
from datetime import datetime, timedelta, timezone

def create_token(uid: str, email: str = "test@example.com"):
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode = {"exp": expire, "sub": uid, "email": email, "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    print(encoded_jwt)

if __name__ == "__main__":
    create_token("93a00f1de3cc4e9d90e32f4ba490263f")
