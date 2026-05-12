from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


class TokenCipher:
    def __init__(self, key: str) -> None:
        self._fernet = Fernet(key.encode())

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        try:
            return self._fernet.decrypt(value.encode()).decode()
        except InvalidToken as exc:
            raise ValueError("Invalid encrypted token") from exc


def get_token_cipher() -> TokenCipher:
    return TokenCipher(settings.encryption_key)
