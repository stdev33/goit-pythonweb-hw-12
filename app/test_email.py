from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.email import send_verification_email
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
print("SECRET_KEY: " + SECRET_KEY)
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


def create_verification_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    data = {"sub": email, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def test_register_user():
    user_email = "stdev@live.ru"
    verification_token = create_verification_token(user_email)

    print("verification_token: " + verification_token)
    send_verification_email(user_email, verification_token)


if __name__ == "__main__":
    test_register_user()
