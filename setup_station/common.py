"""
Contains the data class and some commonly used variables for setup-station
"""
import re
import warnings
import os
import gettext

be_name: str = "default"
logo: str = "/usr/local/lib/setup-station/image/logo.png"
gif_logo: str = "/usr/local/lib/setup-station/image/G_logo.gif"
pc_sysinstall: str = "/usr/local/sbin/pc-sysinstall"
tmp: str = "/tmp/.setup-station"
css_path: str = "/usr/local/lib/setup-station/ghostbsd-style.css"


class SetupData:
    """
    Centralized data storage for setup configuration
    """
    # Language and keyboard configuration
    language: str = ""
    keyboard_layout: str = ""
    keyboard_variant: str = ""
    keyboard_model: str = ""
    
    # Timezone configuration
    timezone: str = ""
    
    # Network configuration
    network_interface: str = ""
    network_config: dict = {}
    
    # User configuration
    username: str = ""
    user_fullname: str = ""
    user_password: str = ""
    user_shell: str = "/usr/local/bin/fish"
    user_home_directory: str = ""
    hostname: str = ""
    
    # Root password (same as user password for setup-station)
    root_password: str = ""
    
    @classmethod
    def reset(cls) -> None:
        """Reset all setup data"""
        cls.language = ""
        cls.keyboard_layout = ""
        cls.keyboard_variant = ""
        cls.keyboard_model = ""
        cls.timezone = ""
        cls.network_interface = ""
        cls.network_config = {}
        cls.username = ""
        cls.user_fullname = ""
        cls.user_password = ""
        cls.user_shell = "/usr/local/bin/fish"
        cls.user_home_directory = ""
        cls.hostname = ""
        cls.root_password = ""


# Default zfs datasets layout
zfs_datasets = "/," \
    "/home(mountpoint=/home)," \
    "/tmp(mountpoint=/tmp|exec=on|setuid=off)," \
    "/usr(mountpoint=/usr|canmount=off)," \
    "/usr/ports(setuid=off)," \
    "/usr/src," \
    "/var(mountpoint=/var|canmount=off)," \
    "/var/audit(exec=off|setuid=off)," \
    "/var/crash(exec=off|setuid=off)," \
    "/var/log(exec=off|setuid=off)," \
    "/var/mail(atime=on)," \
    "/var/tmp(setuid=off)"


def lower_case(text: str) -> bool:
    """
    Find if password contain only lower case.
    :param text: password

    :return: True if password contain only lower case
    """
    search = re.compile(r'[^a-z]').search
    return not bool(search(text))


# Find if password contain only upper case
def upper_case(text: str) -> bool:
    """
    Find if password contain only upper case.
    :param text: password

    :return: True if password contain only upper case
    """
    search = re.compile(r'[^A-Z]').search
    return not bool(search(text))


# Find if password contain only lower case and number
def lower_and_number(text: str) -> bool:
    """
    Find if password contain only lower case and number.
    :param text: password

    :return: True if password contain only lower case and number
    """
    search = re.compile(r'[^a-z0-9]').search
    return not bool(search(text))


# Find if password contain only upper case and number
def upper_and_number(text: str) -> bool:
    """
    Find if password contain only upper case and number.
    :param text: password

    :return: True if password contain only upper case and number
    """
    search = re.compile(r'[^A-Z0-9]').search
    return not bool(search(text))


# Find if password contain only lower and upper case and
def lower_upper(text: str) -> bool:
    """
    Find if password contain only lower and upper case and
    :param text: password

    :return: True if password contain only lower and upper case and
    """
    search = re.compile(r'[^a-zA-Z]').search
    return not bool(search(text))


# Find if password contain only lower and upper case and
def lower_upper_number(text) -> bool:
    """
    Find if password contain only lower and upper case and
    :param text: password

    :return: True if password contain only lower and upper case and
    """
    search = re.compile(r'[^a-zA-Z0-9]').search
    return not bool(search(text))


# Find if password contain only lowercase, uppercase numbers
# and some special character.
def all_character(text):
    """
    Find if password contain only lowercase, uppercase numbers
    and some special character.
    :param text: password

    :return: True if password contain only lowercase, uppercase numbers
    and some special character.
    """
    search = re.compile(r'[^a-zA-Z0-9~!@#$%^&*_+":;\'-]').search
    return not bool(search(text))


def password_strength(password, label3):
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
    if ' ' in password or '\t' in password:
        label3.set_text("Space not allowed")
    elif len(password) <= 4:
        label3.set_text("Super Weak")
    elif len(password) <= 8 and same_character_type:
        label3.set_text("Super Weak")
    elif len(password) <= 8 and mix_character:
        label3.set_text("Very Weak")
    elif len(password) <= 8 and lower_upper_number(password):
        label3.set_text("Fairly Weak")
    elif len(password) <= 8 and all_character(password):
        label3.set_text("Weak")
    elif len(password) <= 12 and same_character_type:
        label3.set_text("Very Weak")
    elif len(password) <= 12 and mix_character:
        label3.set_text("Fairly Weak")
    elif len(password) <= 12 and lower_upper_number(password):
        label3.set_text("Weak")
    elif len(password) <= 12 and all_character(password):
        label3.set_text("Strong")
    elif len(password) <= 16 and same_character_type:
        label3.set_text("Fairly Weak")
    elif len(password) <= 16 and mix_character:
        label3.set_text("Weak")
    elif len(password) <= 16 and lower_upper_number(password):
        label3.set_text("Strong")
    elif len(password) <= 16 and all_character(password):
        label3.set_text("Fairly Strong")
    elif len(password) <= 20 and same_character_type:
        label3.set_text("Weak")
    elif len(password) <= 20 and mix_character:
        label3.set_text("Strong")
    elif len(password) <= 20 and lower_upper_number(password):
        label3.set_text("Fairly Strong")
    elif len(password) <= 20 and all_character(password):
        label3.set_text("Very Strong")
    elif len(password) <= 24 and same_character_type:
        label3.set_text("Strong")
    elif len(password) <= 24 and mix_character:
        label3.set_text("Fairly Strong")
    elif len(password) <= 24 and lower_upper_number(password):
        label3.set_text("Very Strong")
    elif len(password) <= 24 and all_character(password):
        label3.set_text("Super Strong")
    elif same_character_type:
        label3.set_text("Fairly Strong")
    else:
        label3.set_text("Super Strong")


def deprecated(*, version: str, reason: str):
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