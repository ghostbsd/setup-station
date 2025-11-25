import re
import os
from subprocess import run

from data import pc_sysinstall


def replace_pattern(current: str, new: str, file: str) -> None:
    """
    Replace pattern in file with proper error handling.

    Args:
        current: Pattern to search for (regex)
        new: Replacement string
        file: Path to file to modify

    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file operations fail
    """
    if not os.path.exists(file):
        raise FileNotFoundError(f"File not found: {file}")

    try:
        # Read file content
        with open(file, 'r') as f:
            content = f.read()

        # Apply pattern replacement
        modified_content = re.sub(current, new, content)

        # Write modified content back
        with open(file, 'w') as f:
            f.write(modified_content)

    except (IOError, OSError) as e:
        raise IOError(f"Failed to modify file {file}: {e}") from e


def language_dictionary() -> dict:
    """
    Query available system languages from pc-sysinstall.

    Returns:
        dict: Dictionary mapping language names to language codes

    Raises:
        RuntimeError: If pc-sysinstall command fails
    """
    try:
        result = run(
            f'{pc_sysinstall} query-langs',
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
    except Exception as e:
        raise RuntimeError(f"Failed to query languages from pc-sysinstall: {e}") from e

    dictionary = {}
    for line in result.stdout.splitlines():
        lang_list = line.rstrip()
        lang_name = lang_list.partition(' ')[2]
        lang_code = lang_list.partition(' ')[0]
        dictionary[lang_name] = lang_code
    return dictionary


def localize_system(locale: str) -> None:
    """
    Apply locale configuration to the system.

    Args:
        locale: Locale code (e.g., 'en_US', 'fr_FR')

    Raises:
        IOError: If file operations fail
        ValueError: If locale is empty
    """
    if not locale:
        raise ValueError("Locale cannot be empty")

    slick_greeter = "/usr/local/share/xgreeters/slick-greeter.desktop"
    gtk_greeter = "/usr/local/share/xgreeters/lightdm-gtk-greeter.desktop"

    try:
        replace_pattern('lang=C', f'lang={locale}', '/etc/login.conf')
        replace_pattern('en_US', locale, '/etc/profile')
        replace_pattern('en_US', locale, '/usr/share/skel/dot.profile')

        if os.path.exists(slick_greeter):
            replace_pattern(
                'Exec=slick-greeter',
                f'Exec=env LANG={locale}.UTF-8 slick-greeter',
                slick_greeter
            )
        elif os.path.exists(gtk_greeter):
            replace_pattern(
                'Exec=lightdm-gtk-greeter',
                f'Exec=env LANG={locale}.UTF-8 lightdm-gtk-greeter',
                gtk_greeter
            )
    except (IOError, OSError, FileNotFoundError) as e:
        raise IOError(f"Failed to localize system with locale '{locale}': {e}") from e


def keyboard_dictionary() -> dict:
    """
    Query available keyboard layouts and variants from pc-sysinstall.

    Returns:
        dict: Dictionary mapping keyboard names to layout/variant info

    Raises:
        RuntimeError: If pc-sysinstall command fails
    """
    try:
        # Get keyboard layouts
        result1 = run(
            f'{pc_sysinstall} xkeyboard-layouts',
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )

        dictionary = {}
        for line in result1.stdout.splitlines():
            keyboard_list = list(filter(None, line.rstrip().split('  ')))
            kb_name = keyboard_list[1].strip()
            kb_layouts = keyboard_list[0].strip()
            kb_variant = None
            dictionary[kb_name] = {'layout': kb_layouts, 'variant': kb_variant}

        # Get keyboard variants
        result2 = run(
            f'{pc_sysinstall} xkeyboard-variants',
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )

        for line in result2.stdout.splitlines():
            xkb_variant = line.rstrip()
            kb_name = xkb_variant.partition(':')[2].strip()
            keyboard_list = list(filter
                                 (None, xkb_variant.partition(':')[0].split()))
            kb_layouts = keyboard_list[1].strip()
            kb_variant = keyboard_list[0].strip()
            dictionary[kb_name] = {'layout': kb_layouts, 'variant': kb_variant}
        return dictionary
    except Exception as e:
        raise RuntimeError(f"Failed to query keyboard layouts from pc-sysinstall: {e}") from e


def keyboard_models() -> dict:
    """
    Query available keyboard models from pc-sysinstall.

    Returns:
        dict: Dictionary mapping keyboard model names to model codes

    Raises:
        RuntimeError: If pc-sysinstall command fails
    """
    try:
        result = run(
            f'{pc_sysinstall} xkeyboard-models',
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )

        dictionary = {}
        for line in result.stdout.splitlines():
            kbm_name = line.rstrip().partition(' ')[2]
            kbm_code = line.rstrip().partition(' ')[0]
            dictionary[kbm_name] = kbm_code
        return dictionary
    except Exception as e:
        raise RuntimeError(f"Failed to query keyboard models from pc-sysinstall: {e}") from e


def change_keyboard(kb_layout: str, kb_variant: str = None, kb_model: str = None) -> None:
    """
    Change the current X session keyboard layout immediately.

    Args:
        kb_layout: Keyboard layout code (e.g., 'us', 'fr', 'de')
        kb_variant: Optional keyboard variant
        kb_model: Optional keyboard model

    Raises:
        RuntimeError: If setxkbmap command fails
    """
    try:
        if kb_variant is None and kb_model is not None:
            run(['setxkbmap', '-layout', kb_layout, '-model', kb_model], check=True)
        elif kb_variant is not None and kb_model is None:
            run(['setxkbmap', '-layout', kb_layout, '-variant', kb_variant], check=True)
        elif kb_variant is not None and kb_model is not None:
            run(['setxkbmap', '-layout', kb_layout, '-variant', kb_variant, '-model', kb_model], check=True)
        else:
            run(['setxkbmap', '-layout', kb_layout], check=True)
    except Exception as e:
        raise RuntimeError(f"Failed to change keyboard layout: {e}") from e


def set_keyboard(kb_layout: str = None, kb_variant: str = None, kb_model: str = None) -> None:
    """
    Persistently configure keyboard layout system-wide.
    Configures X11 via xorg.conf.d, console keymap, and desktop environment
    specific settings (MATE/XFCE).

    Args:
        kb_layout: Keyboard layout code (defaults to 'us')
        kb_variant: Optional keyboard variant
        kb_model: Optional keyboard model (defaults to 'pc104')

    Raises:
        IOError: If file operations fail
        RuntimeError: If subprocess commands fail
    """
    kx_model = kb_model if kb_model else "pc104"
    kx_layout = kb_layout if kb_layout else "us"

    try:
        # Configure X11 keyboard layout via xorg.conf.d
        # This affects X server, lightdm greeter, and all X sessions
        xorg_kbd_conf = "/usr/local/etc/X11/xorg.conf.d/00-keyboard.conf"
        os.makedirs(os.path.dirname(xorg_kbd_conf), exist_ok=True)

        with open(xorg_kbd_conf, 'w') as f:
            f.write('Section "InputClass"\n')
            f.write('    Identifier "system-keyboard"\n')
            f.write('    MatchIsKeyboard "on"\n')
            f.write(f'    Option "XkbLayout" "{kx_layout}"\n')
            if kb_variant:
                f.write(f'    Option "XkbVariant" "{kb_variant}"\n')
            f.write(f'    Option "XkbModel" "{kx_model}"\n')
            f.write('EndSection\n')

        # Set console keyboard layout in rc.conf
        if kb_layout:
            # Map X11 layouts to console keymaps
            console_keymap_map = {
                'ca': 'ca-fr.kbd',
                'et': 'ee.kbd',
                'es': 'es.acc.kbd',
                'gb': 'uk.kbd'
            }

            console_keymap = console_keymap_map.get(kb_layout, f"{kb_layout}.kbd")
            run(['sysrc', f'keymap={console_keymap}'], check=True)

        # Configure MATE keyboard settings
        mate_schema = "/usr/local/share/glib-2.0/schemas/org.mate.peripherals-keyboard-xkb.gschema.xml"
        if os.path.exists(mate_schema):
            override_file = "/usr/local/share/glib-2.0/schemas/92_org.mate.peripherals-keyboard-xkb.kbd.gschema.override"
            option = "grp:alt_shift_toggle"

            with open(override_file, 'w') as f:
                f.write("[org.mate.peripherals-keyboard-xkb.kbd]\n")
                if kb_variant:
                    f.write(f"layouts=['{kx_layout}\\t{kb_variant}']\n")
                else:
                    f.write(f"layouts=['{kx_layout}']\n")
                f.write(f"model='{kx_model}'\n")
                f.write(f"options=['{option}']\n")

            # Compile schemas
            run(['glib-compile-schemas', '/usr/local/share/glib-2.0/schemas/'], check=True)

        # Configure XFCE keyboard settings
        xfce_kb_xml = "/usr/local/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/keyboard-layout.xml"
        if os.path.exists(xfce_kb_xml):
            replace_pattern('value="us"', f'value="{kx_layout}"', xfce_kb_xml)
            if kb_variant:
                replace_pattern('value=""', f'value="{kb_variant}"', xfce_kb_xml)

    except (IOError, OSError) as e:
        raise IOError(f"Failed to configure keyboard layout: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to set keyboard configuration: {e}") from e


def timezone_dictionary() -> dict:
    """
    Query available timezones from pc-sysinstall.

    Returns:
        dict: Dictionary mapping continents to lists of cities

    Raises:
        RuntimeError: If pc-sysinstall command fails
    """
    try:
        result = run(
            [pc_sysinstall, 'list-tzones'],
            capture_output=True,
            text=True,
            check=True
        )

        dictionary = {}
        for zone in result.stdout.splitlines():
            zone_list = zone.partition(':')[0].rstrip().split('/')
            if len(zone_list) < 2:
                continue

            continent = zone_list[0]
            city = '/'.join(zone_list[1:])
            dictionary.setdefault(continent, []).append(city)
        return dictionary
    except Exception as e:
        raise RuntimeError(f"Failed to query timezones from pc-sysinstall: {e}") from e


def set_timezone(timezone: str) -> None:
    """
    Set the system timezone by copying the appropriate zoneinfo file.

    Args:
        timezone: Timezone string (e.g., 'America/New_York', 'Europe/London')

    Raises:
        ValueError: If timezone is invalid, contains path traversal, or not found
        RuntimeError: If timezone copy command fails
    """
    if not timezone:
        raise ValueError("Timezone cannot be empty")

    # Validate timezone doesn't contain path traversal or absolute paths
    if '..' in timezone or timezone.startswith('/'):
        raise ValueError(f"Invalid timezone: '{timezone}'. Path traversal not allowed.")

    # Validate timezone format (continent/city or continent/region/city)
    import re
    if not re.match(r'^[A-Za-z_]+(/[A-Za-z_+-]+)+$', timezone):
        raise ValueError(f"Invalid timezone format: '{timezone}'. Expected format: Continent/City")

    zoneinfo_path = f"/usr/share/zoneinfo/{timezone}"
    localtime_path = "/etc/localtime"

    if not os.path.exists(zoneinfo_path):
        raise ValueError(f"Timezone '{timezone}' not found in /usr/share/zoneinfo/")

    try:
        run(['cp', zoneinfo_path, localtime_path], check=True)
    except Exception as e:
        raise RuntimeError(f"Failed to set timezone '{timezone}': {e}") from e


def set_admin_user(username: str, name: str, password: str, shell: str, homedir: str, hostname: str) -> None:
    """
    Create admin user and set passwords securely.

    Args:
        username: Username for the admin account (alphanumeric, underscore, dash)
        name: Full name of the user
        password: Password for both root and admin user
        shell: Path to the user's shell (must exist in /etc/shells)
        homedir: Home directory path (no path traversal)
        hostname: System hostname (valid hostname format)

    Raises:
        ValueError: If input validation fails
        subprocess.CalledProcessError: If any command fails

    Note: Password is passed via stdin to avoid exposure in process list.
    """
    import re

    # Validate username format (alphanumeric, underscore, dash, starts with letter or underscore)
    if not username or not re.match(r'^[a-z_][a-z0-9_-]*$', username, re.IGNORECASE):
        raise ValueError(f"Invalid username format: '{username}'. Must start with letter/underscore and contain only alphanumeric, underscore, or dash.")

    # Validate username length
    if len(username) > 32:
        raise ValueError(f"Username too long: '{username}'. Maximum 32 characters.")

    # Validate name is not empty
    if not name or not name.strip():
        raise ValueError("Full name cannot be empty")

    # Validate password is not empty
    if not password:
        raise ValueError("Password cannot be empty")

    # Validate shell exists in /etc/shells
    if shell:
        try:
            with open('/etc/shells', 'r') as f:
                valid_shells = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if shell not in valid_shells:
                raise ValueError(f"Invalid shell: '{shell}'. Must be listed in /etc/shells")
        except FileNotFoundError:
            pass  # /etc/shells might not exist, let pw command handle it

    # Validate homedir path (no path traversal)
    if homedir and ('..' in homedir or not homedir.startswith('/')):
        raise ValueError(f"Invalid home directory path: '{homedir}'. Must be absolute path without '..'")

    # Validate hostname format (RFC 1123)
    if hostname and not re.match(r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*$', hostname, re.IGNORECASE):
        raise ValueError(f"Invalid hostname format: '{hostname}'. Must follow RFC 1123 hostname rules.")

    # Set Root user password (password read from stdin with -h 0)
    run(
        ['pw', 'usermod', '-n', 'root', '-h', '0'],
        input=password,
        text=True,
        check=True
    )

    # Create admin user with password from stdin
    run(
        [
            'pw', 'useradd', username,
            '-c', name,
            '-h', '0',
            '-s', shell,
            '-m',
            '-d', homedir,
            '-G', 'wheel,operator'
        ],
        input=password,
        text=True,
        check=True
    )

    # Set hostname
    run(['sysrc', f'hostname={hostname}'], check=True)
    run(['hostname', hostname], check=True)
