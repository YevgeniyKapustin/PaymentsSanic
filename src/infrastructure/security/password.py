from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt and return the password hash.

    This function is intentionally small and uses a centralized password
    context so the hashing scheme can be configured in one place.

    Args:
        password: Plain-text password to hash.

    Returns:
        The bcrypt password hash as a string.
    """
    # passlib returns an implementation-defined str-like object; coerce to str for type checkers
    return str(pwd_context.hash(password))


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plain-text password against a stored hash.

    Args:
        password: Plain-text password to verify.
        password_hash: Stored bcrypt hash to verify against.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    # pwd_context.verify may be untyped; coerce result to bool for mypy
    return bool(pwd_context.verify(password, password_hash))
