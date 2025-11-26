"""
Password validation utilities for setup-station and setup-station-init.
"""
import re
import warnings


def lower_case(text: str) -> bool:
    """
    Check if password contains only lowercase letters.

    Args:
        text: Password string to validate

    Returns:
        bool: True if password contains only lowercase letters (a-z)
    """
    search = re.compile(r'[^a-z]').search
    return not bool(search(text))


def upper_case(text: str) -> bool:
    """
    Check if password contains only uppercase letters.

    Args:
        text: Password string to validate

    Returns:
        bool: True if password contains only uppercase letters (A-Z)
    """
    search = re.compile(r'[^A-Z]').search
    return not bool(search(text))


def lower_and_number(text: str) -> bool:
    """
    Check if password contains only lowercase letters and numbers.

    Args:
        text: Password string to validate

    Returns:
        bool: True if password contains only lowercase letters (a-z) and digits (0-9)
    """
    search = re.compile(r'[^a-z0-9]').search
    return not bool(search(text))


def upper_and_number(text: str) -> bool:
    """
    Check if password contains only uppercase letters and numbers.

    Args:
        text: Password string to validate

    Returns:
        bool: True if password contains only uppercase letters (A-Z) and digits (0-9)
    """
    search = re.compile(r'[^A-Z0-9]').search
    return not bool(search(text))


def lower_upper(text: str) -> bool:
    """
    Check if password contains only lowercase and uppercase letters.

    Args:
        text: Password string to validate

    Returns:
        bool: True if password contains only letters (a-z, A-Z) without numbers or special characters
    """
    search = re.compile(r'[^a-zA-Z]').search
    return not bool(search(text))


def lower_upper_number(text: str) -> bool:
    """
    Check if password contains only letters and numbers.

    Args:
        text: Password string to validate

    Returns:
        bool: True if password contains only letters (a-z, A-Z) and digits (0-9) without special characters
    """
    search = re.compile(r'[^a-zA-Z0-9]').search
    return not bool(search(text))


def all_character(text: str) -> bool:
    """
    Check if password contains letters, numbers, and allowed special characters.

    Args:
        text: Password string to validate

    Returns:
        bool: True if password contains only allowed characters (a-z, A-Z, 0-9, and ~!@#$%^&*_+":;'-)
    """
    search = re.compile(r'[^a-zA-Z0-9~!@#$%^&*_+":;\'-]').search
    return not bool(search(text))


def password_strength(password: str) -> str:
    """
    Evaluate password strength and return the message.

    Args:
        password: The password to evaluate

    Returns:
        str: Message describing password strength or validation error
    """

    same_character_type = any(
        [
            lower_case(password),
            upper_case(password),
            password.isdigit()
        ]
    )
    mix_character = any(
        [
            lower_and_number(password),
            upper_and_number(password),
            lower_upper(password)
        ]
    )

    # Passwords that should not be allowed
    not_allowed = {'password', 'Password', 'PASSWORD'}

    # Check if a password is not allowed
    if password in not_allowed:
        return "Password not allowed"
    elif ' ' in password or '\t' in password:
        return "Space not allowed"
    elif len(password) <= 4:
        return "Super Weak"
    elif len(password) <= 8 and same_character_type:
        return "Super Weak"
    elif len(password) <= 8 and mix_character:
        return "Very Weak"
    elif len(password) <= 8 and lower_upper_number(password):
        return "Fairly Weak"
    elif len(password) <= 8 and all_character(password):
        return "Weak"
    elif len(password) <= 12 and same_character_type:
        return "Very Weak"
    elif len(password) <= 12 and mix_character:
        return "Fairly Weak"
    elif len(password) <= 12 and lower_upper_number(password):
        return "Weak"
    elif len(password) <= 12 and all_character(password):
        return "Strong"
    elif len(password) <= 16 and same_character_type:
        return "Fairly Weak"
    elif len(password) <= 16 and mix_character:
        return "Weak"
    elif len(password) <= 16 and lower_upper_number(password):
        return "Strong"
    elif len(password) <= 16 and all_character(password):
        return "Fairly Strong"
    elif len(password) <= 20 and same_character_type:
        return "Weak"
    elif len(password) <= 20 and mix_character:
        return "Strong"
    elif len(password) <= 20 and lower_upper_number(password):
        return "Fairly Strong"
    elif len(password) <= 20 and all_character(password):
        return "Very Strong"
    elif len(password) <= 24 and same_character_type:
        return "Strong"
    elif len(password) <= 24 and mix_character:
        return "Fairly Strong"
    elif len(password) <= 24 and lower_upper_number(password):
        return "Very Strong"
    elif len(password) <= 24 and all_character(password):
        return "Super Strong"
    elif same_character_type:
        return "Fairly Strong"
    else:
        return "Super Strong"


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