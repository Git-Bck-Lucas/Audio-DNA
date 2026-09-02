from cryptography.fernet import Fernet
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from backend.config import settings

_fernet = Fernet(settings.TOKEN_ENCRYPTION_KEY.encode())


class EncryptedString(TypeDecorator):
    """String-Spalte, die beim Schreiben verschlüsselt und beim Lesen entschlüsselt wird.

    Fernet nutzt pro Aufruf einen zufälligen Nonce, d.h. derselbe Klartext ergibt bei
    jedem encrypt() ein anderes Chiffrat. Ein unique-Constraint auf so einer Spalte
    prüft dadurch faktisch nichts mehr und sollte nicht verwendet werden.
    """

    impl = String
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        if value is None:
            return None
        return _fernet.encrypt(value.encode()).decode()

    def process_result_value(self, value: str | None, dialect) -> str | None:
        if value is None:
            return None
        return _fernet.decrypt(value.encode()).decode()
