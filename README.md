# Setup Station

Setup Station does the initial setup of GhostBSD. The goal is to evolve Setup Station to slowly replace MATE Configuration Tool and Station Tweak, providing a unified configuration experience.

## Overview

Setup Station is a GTK3-based Python application that runs automatically after GhostBSD installation to guide users through essential system configuration:

- System language and locale
- Keyboard layout and variant
- Timezone
- Network settings (WiFi/Ethernet)
- Admin user account creation

After completing the setup, the system automatically starts the LightDM login screen.

## Installation

```bash
python setup.py install
```

## Running Setup Station

```bash
sudo setup-station-init
```

## Managing Translations

Setup Station uses GNU gettext for internationalization.

### Creating a new translation

```bash
./setup.py create_translation --locale=<language_code>
```

Example for French (France):
```bash
./setup.py create_translation --locale=fr_FR
```

### Updating existing translations

After modifying source code with new or changed translatable strings:

```bash
./setup.py update_translations
```

### Building translations

```bash
./setup.py build_i18n
```

## Contributing

Interested in contributing to Setup Station or other GhostBSD tools?

- Join our Telegram channel: https://t.me/ghostbsd_dev
- Discuss on GitHub: https://github.com/orgs/ghostbsd/discussions/categories/tools-and-softwares

## License

BSD 3-Clause License

## Links

- GitHub: https://github.com/GhostBSD/setup-station/
- GhostBSD: https://www.ghostbsd.org/
