import re
import os
from subprocess import Popen, run, PIPE

pc_sysinstall = '/usr/local/sbin/pc-sysinstall'


def replace_pattern(current, new, file):
    parser_file = open(file, 'r').read()
    parser_patched = re.sub(current, new, parser_file)
    save_parser_file = open(file, 'w')
    save_parser_file.writelines(parser_patched)
    save_parser_file.close()


def language_dictionary():
    langs = Popen(f'{pc_sysinstall} query-langs', shell=True, stdin=PIPE,
                  stdout=PIPE, universal_newlines=True,
                  close_fds=True).stdout.readlines()
    dictionary = {}
    for line in langs:
        lang_list = line.rstrip()
        lang_name = lang_list.partition(' ')[2]
        lang_code = lang_list.partition(' ')[0]
        dictionary[lang_name] = lang_code
    return dictionary


def localize_system(locale):
    slick_greeter = "/usr/local/share/xgreeters/slick-greeter.desktop"
    gtk_greeter = "/usr/local/share/xgreeters/lightdm-gtk-greeter.desktop"
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
            'Exec=lightdm-gtk-greete',
            f'Exec=env LANG={locale}.UTF-8 lightdm-gtk-greeter',
            gtk_greeter
        )


def keyboard_dictionary():
    xkeyboard_layouts = Popen(f'{pc_sysinstall} xkeyboard-layouts', shell=True,
                              stdout=PIPE,
                              universal_newlines=True).stdout.readlines()
    dictionary = {}
    for line in xkeyboard_layouts:
        keyboard_list = list(filter(None, line.rstrip().split('  ')))
        kb_name = keyboard_list[1].strip()
        kb_layouts = keyboard_list[0].strip()
        kb_variant = None
        dictionary[kb_name] = {'layout': kb_layouts, 'variant': kb_variant}

    xkeyboard_variants = Popen(f'{pc_sysinstall} xkeyboard-variants',
                               shell=True, stdout=PIPE,
                               universal_newlines=True).stdout.readlines()
    for line in xkeyboard_variants:
        xkb_variant = line.rstrip()
        kb_name = xkb_variant.partition(':')[2].strip()
        keyboard_list = list(filter
                             (None, xkb_variant.partition(':')[0].split()))
        kb_layouts = keyboard_list[1].strip()
        kb_variant = keyboard_list[0].strip()
        dictionary[kb_name] = {'layout': kb_layouts, 'variant': kb_variant}
    return dictionary


def keyboard_models():
    xkeyboard_models = Popen(f'{pc_sysinstall} xkeyboard-models', shell=True,
                             stdout=PIPE,
                             universal_newlines=True).stdout.readlines()
    dictionary = {}
    for line in xkeyboard_models:
        kbm_name = line.rstrip().partition(' ')[2]
        kbm_code = line.rstrip().partition(' ')[0]
        dictionary[kbm_name] = kbm_code
    return dictionary


def change_keyboard(kb_layout, kb_variant=None, kb_model=None):
    if kb_variant is None and kb_model is not None:
        run(f"setxkbmap -layout {kb_layout} -model {kb_model}", shell=True)
    elif kb_variant is not None and kb_model is None:
        run(f"setxkbmap -layout {kb_layout} -variant {kb_variant}", shell=True)
    elif kb_variant is not None and kb_model is not None:
        set_kb_cmd = f"setxkbmap -layout {kb_layout} -variant {kb_variant} " \
            f"-model {kb_model}"
        run(set_kb_cmd, shell=True)
    else:
        run(f"setxkbmap -layout {kb_layout}", shell=True)


def set_keyboard(kb_layout, kb_variant=None, kb_model=None):
    """
    Persistently configure keyboard layout system-wide.
    Sets up X11 keyboard via .xprofile, lightdm greeter, console keymap,
    and desktop environment specific configs (MATE/XFCE).
    """
    # Build setxkbmap command
    setxkbmap_cmd = ""
    kx_model = kb_model if kb_model else "pc104"
    kx_layout = kb_layout if kb_layout else "us"

    if kb_model:
        setxkbmap_cmd = f"-model {kb_model}"

    if kb_layout:
        setxkbmap_cmd = f"{setxkbmap_cmd} -layout {kb_layout}".strip()

    if kb_variant:
        setxkbmap_cmd = f"{setxkbmap_cmd} -variant {kb_variant}"

    # Set up .xprofile for user X sessions
    if setxkbmap_cmd:
        xprofile_path = "/usr/share/skel/.xprofile"

        # Create or update .xprofile
        if not os.path.exists(xprofile_path):
            with open(xprofile_path, 'w') as f:
                f.write("#!/bin/sh\n")

        # Append setxkbmap command
        with open(xprofile_path, 'a') as f:
            f.write(f"setxkbmap {setxkbmap_cmd}\n")

        # Make executable
        os.chmod(xprofile_path, 0o755)

        # Copy to root's home
        run(f"cp {xprofile_path} /root/.xprofile", shell=True)

        # Configure lightdm greeter
        lightdm_conf = "/usr/local/etc/lightdm/lightdm.conf"
        if os.path.exists(lightdm_conf):
            replace_pattern(
                '#greeter-setup-script=',
                f'greeter-setup-script=setxkbmap {setxkbmap_cmd}',
                lightdm_conf
            )

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
        run(f'sysrc keymap="{console_keymap}"', shell=True)

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
        run("glib-compile-schemas /usr/local/share/glib-2.0/schemas/", shell=True)

    # Configure XFCE keyboard settings
    xfce_kb_xml = "/usr/local/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/keyboard-layout.xml"
    if os.path.exists(xfce_kb_xml):
        replace_pattern('value="us"', f'value="{kx_layout}"', xfce_kb_xml)
        if kb_variant:
            replace_pattern('value=""', f'value="{kb_variant}"', xfce_kb_xml)


def timezone_dictionary():
    tz_list = Popen(f'{pc_sysinstall} list-tzones', shell=True,
                    stdout=PIPE, universal_newlines=True).stdout.readlines()
    city_list = []
    dictionary = {}
    last_continent = ''
    for zone in tz_list:
        zone_list = zone.partition(':')[0].rstrip().split('/')
        continent = zone_list[0]
        if continent != last_continent:
            city_list = []
        if len(zone_list) == 3:
            city = zone_list[1] + '/' + zone_list[2]
        elif len(zone_list) == 4:
            city = zone_list[1] + '/' + zone_list[2] + '/' + zone_list[3]
        else:
            city = zone_list[1]
        city_list.append(city)
        dictionary[continent] = city_list
        last_continent = continent
    return dictionary


def set_timezone(timezone):
    """
    Set the system timezone by copying the appropriate zoneinfo file.

    Args:
        timezone: Timezone string (e.g., 'America/New_York', 'Europe/London')
    """
    zoneinfo_path = f"/usr/share/zoneinfo/{timezone}"
    localtime_path = "/etc/localtime"

    if os.path.exists(zoneinfo_path):
        run(f"cp {zoneinfo_path} {localtime_path}", shell=True)
    else:
        raise ValueError(f"Timezone '{timezone}' not found in /usr/share/zoneinfo/")


def set_admin_user(username, name, password, shell, homedir, hostname):
    # Set Root user
    run(f"echo '{password}' | pw usermod -n root -h 0", shell=True)
    cmd = f"echo '{password}' | pw useradd {username} -c {name} -h 0" \
        f" -s {shell} -m -d {homedir} -g wheel,operator"
    run(cmd, shell=True)
    run(f"sysrc hostname={hostname}", shell=True)
    run(f"hostname {hostname}", shell=True)
