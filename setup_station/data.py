"""
Contains the data class and some commonly used variables for setup-station-init
"""
import os
import gettext

logo: str = "/usr/local/lib/setup-station-init/image/logo.png"
gif_logo: str = "/usr/local/lib/setup-station-init/image/G_logo.gif"
pc_sysinstall: str = "/usr/local/sbin/pc-sysinstall"
tmp: str = "/tmp/.setup-station-init"
css_path: str = "/usr/local/lib/setup-station-init/ghostbsd-style.css"


class SetupData:
    """
    Centralized data storage for setup configuration
    """
    # Language and localization
    language: str = ""
    language_code: str = ""
    
    # Keyboard configuration
    keyboard_layout: str = ""
    keyboard_layout_code: str = ""
    keyboard_variant: str = ""
    keyboard_model: str = ""
    keyboard_model_code: str = ""
    
    # Timezone configuration
    timezone: str = ""
    
    # Network configuration
    network_config: dict = {}

    # Admin user configuration
    username: str = ""
    user_fullname: str = ""
    user_password: str = ""
    user_shell: str = ""
    user_home_directory: str = ""
    hostname: str = ""
    root_password: str = ""

    @classmethod
    def reset(cls) -> None:
        """Reset all setup data"""
        cls.language = ""
        cls.language_code = ""
        cls.keyboard_layout = ""
        cls.keyboard_layout_code = ""
        cls.keyboard_variant = ""
        cls.keyboard_model = ""
        cls.keyboard_model_code = ""
        cls.timezone = ""
        cls.network_config = {}
        cls.username = ""
        cls.user_fullname = ""
        cls.user_password = ""
        cls.user_shell = ""
        cls.user_home_directory = ""
        cls.hostname = ""
        cls.root_password = ""


def get_text(text: str) -> str:
    """
    Global translation function that always returns current language translation.
    
    Args:
        text: Text to translate
        
    Returns:
        str: Translated text in current language
    """
    # Force reload of translations for current language
    gettext.bindtextdomain('setup-station-init', '/usr/local/share/locale')
    gettext.textdomain('setup-station-init')
    return gettext.gettext(text)