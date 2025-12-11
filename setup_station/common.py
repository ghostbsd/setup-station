"""
Password validation utilities for setup-station and setup-station-init.
"""
import re
import warnings
from setup_station.data import get_text


def is_same_type(text: str) -> bool:
    """
    Check if password contains only one character type.

    Args:
        text: Password string to validate

    Returns:
        bool: True if password is all lowercase, all uppercase, or all digits
    """
    # ^[a-z]+$ - only lowercase letters from start to end
    # ^[A-Z]+$ - only uppercase letters from start to end
    # ^[0-9]+$ - only digits from start to end
    return bool(re.match(r'^[a-z]+$|^[A-Z]+$|^[0-9]+$', text))


def mix_character(text: str) -> bool:
    """
    Check if password contains exactly two character types.

    Args:
        text: Password string to validate

    Returns:
        bool: True if password contains lower+number, upper+number, or lower+upper
    """
    # ^(?=.*[a-z])(?=.*[0-9])[a-z0-9]+$ - must have at least one lowercase AND one digit, only lowercase/digits allowed
    # ^(?=.*[A-Z])(?=.*[0-9])[A-Z0-9]+$ - must have at least one uppercase AND one digit, only uppercase/digits allowed
    # ^(?=.*[a-z])(?=.*[A-Z])[a-zA-Z]+$ - must have at least one lowercase AND one uppercase, only letters allowed
    return bool(
        re.match(
            r'^(?=.*[a-z])(?=.*[0-9])[a-z0-9]+$|^(?=.*[A-Z])(?=.*[0-9])[A-Z0-9]+$|^(?=.*[a-z])(?=.*[A-Z])[a-zA-Z]+$',
            text
        )
    )


def lower_upper_number(text: str) -> bool:
    """
    Check if password contains letters and numbers (three character types).

    Args:
        text: Password string to validate

    Returns:
        bool: True if password contains lowercase, uppercase, and digits
    """
    # ^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])[a-zA-Z0-9]+$ - must have lowercase AND uppercase AND digit,
    # only letters/digits allowed
    return bool(re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])[a-zA-Z0-9]+$', text))


def all_character(text: str) -> bool:
    """
    Check if password contains letters, numbers, and special characters.

    Args:
        text: Password string to validate

    Returns:
        bool: True if password contains lowercase, uppercase, digits, and special characters
    """
    # ^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[~!@#$%^&*_+":;\'-])[a-zA-Z0-9~!@#$%^&*_+":;\'-]+$
    # must have lowercase AND uppercase AND digit AND special char, only those characters allowed
    return bool(
        re.match(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[~!@#$%^&*_+":;\'-])[a-zA-Z0-9~!@#$%^&*_+":;\'-]+$',
            text
        )
    )


def _get_complexity_tier(password: str) -> int:
    """
    Determine password complexity tier based on character type diversity.

    Args:
        password: The password to evaluate

    Returns:
        int: Complexity tier (0-3)
            0 = single character type (all lowercase, all uppercase, or all digits)
            1 = two character types (lower+number, upper+number, or lower+upper)
            2 = three character types (letters + numbers)
            3 = all character types (letters + numbers + special chars)
    """
    if all_character(password):
        return 3
    if lower_upper_number(password):
        return 2
    if mix_character(password):
        return 1
    return 0


def password_strength(password: str) -> str:
    """
    Evaluate password strength and return the message.

    Uses structural pattern matching to determine strength based on
    password length and character complexity.

    Args:
        password: The password to evaluate

    Returns:
        str: Message describing password strength or validation error
    """
    # Guard clauses for invalid passwords
    if password in {'password', 'Password', 'PASSWORD'}:
        return get_text("Password not allowed")
    if ' ' in password or '\t' in password:
        return get_text("Space not allowed")

    # Determine length range
    length = len(password)
    if length <= 8:
        length_range = 8
    elif length <= 12:
        length_range = 12
    elif length <= 15:
        length_range = 15
    else:
        length_range = 16

    complexity = _get_complexity_tier(password)

    # Pattern matching for strength evaluation
    match (length_range, complexity):
        case (8, 0): return get_text("Very Weak")
        case (8, 1): return get_text("Fairly Weak")
        case (8, 2): return get_text("Weak")
        case (8, 3): return get_text("Strong")
        case (12, 0): return get_text("Fairly Weak")
        case (12, 1): return get_text("Weak")
        case (12, 2): return get_text("Strong")
        case (12, 3): return get_text("Fairly Strong")
        case (15, 0): return get_text("Weak")
        case (15, 1): return get_text("Strong")
        case (15, 2): return get_text("Fairly Strong")
        case (15, 3): return get_text("Very Strong")
        case (16, 0): return get_text("Strong")
        case (16, 1): return get_text("Fairly Strong")
        case _: return get_text("Very Strong")


def deprecated(*, version: str, reason: str):
    """
    Decorator to mark functions as deprecated.

    Args:
        version: Version in which the function was deprecated
        reason: Reason for deprecation

    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated (version {version}): {reason}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator