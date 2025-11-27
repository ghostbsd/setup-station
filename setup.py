#!/usr/bin/env python
"""
Setup script for Setup Station.

Setup Station is GhostBSD's post-installation setup utility, providing
a GTK+ interface for language, keyboard, timezone, network, and user configuration.
"""
import os
import sys
from setuptools import setup, Command
import glob
from DistUtilsExtra.command.build_extra import build_extra
from DistUtilsExtra.command.build_i18n import build_i18n
from DistUtilsExtra.command.clean_i18n import clean_i18n

prefix = sys.prefix
__VERSION__ = '0.1'
PROGRAM_VERSION = __VERSION__


def data_file_list(install_base, source_base):
    """
    Generate list of data files for installation.

    Args:
        install_base: Base installation path
        source_base: Source directory to scan

    Returns:
        List of (install_path, files) tuples for setuptools
    """
    data = []
    for root, subFolders, files in os.walk(source_base):
        file_list = []
        for f in files:
            file_list.append(os.path.join(root, f))
        # Only add directories that actually have files
        if file_list:
            data.append((root.replace(source_base, install_base), file_list))
    return data


class UpdateTranslationsCommand(Command):
    """Custom command to extract messages and update .po files."""

    description = 'Extract messages to .pot and update .po'
    user_options = []  # No custom options

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Define paths
        pot_file = 'po/setup-station.pot'
        po_files = glob.glob('po/*.po')

        # Check if .pot file exists, create it if it doesn't
        if not os.path.exists(pot_file):
            print(f"POT file {pot_file} does not exist. Creating it...")
        else:
            print("Updating existing .pot file...")

        # Step 1: Extract messages to .pot file (create or update)
        print("Extracting messages to .pot file...")
        os.makedirs('po', exist_ok=True)
        os.system(
            f'xgettext --from-code=UTF-8 -L Python --keyword=get_text -o {pot_file}'
            ' setup_station/*.py setup-station-init'
        )

        # Verify .pot file was created successfully
        if not os.path.exists(pot_file):
            print(f"Error: Failed to create {pot_file}")
            return

        # Fix charset to UTF-8 in the .pot file
        print("Setting charset to UTF-8 in .pot file...")
        os.system(f"sed -i '' 's/charset=CHARSET/charset=UTF-8/g' {pot_file}")

        # Step 2: Update .po files with the new .pot file
        print("Updating .po files with new translations...")
        for po_file in po_files:
            print(f"Updating {po_file}...")
            os.system(f'msgmerge -U {po_file} {pot_file}')
        print("Translation update complete.")


class CreateTranslationCommand(Command):
    """Custom command to create a new .po file for a specific language."""
    locale = None
    description = 'Create a new .po file for the specified language'
    user_options = [
        ('locale=', 'l', 'Locale code for the new translation (e.g., fr, es)')
    ]

    def initialize_options(self):
        self.locale = None  # Initialize the locale option to None

    def finalize_options(self):
        if self.locale is None:
            raise Exception("You must specify the locale code (e.g., --locale=fr)")

    def run(self):
        # Define paths
        pot_file = 'po/setup-station.pot'
        po_dir = 'po'
        po_file = os.path.join(po_dir, f'{self.locale}.po')
        # Check if the .pot file exists
        if not os.path.exists(pot_file):
            print("Extracting messages to .pot file...")
            os.makedirs(po_dir, exist_ok=True)
            os.system(
                f'xgettext --from-code=UTF-8 -L Python --keyword=get_text -o {pot_file}'
                ' setup_station/*.py setup-station-init'
            )
            # Fix charset to UTF-8 in the .pot file
            print("Setting charset to UTF-8 in .pot file...")
            os.system(f"sed -i '' 's/charset=CHARSET/charset=UTF-8/g' {pot_file}")
        # Create the new .po file
        if not os.path.exists(po_file):
            print(f"Creating new {po_file} for locale '{self.locale}'...")
            os.makedirs(po_dir, exist_ok=True)
            os.system(f'msginit --locale={self.locale} --input={pot_file} --output-file={po_file}')
        else:
            print(f"PO file for locale '{self.locale}' already exists: {po_file}")


lib_setup_station_image = [
    'src/image/G_logo.gif',
    'src/image/install-gbsd.png',
    'src/image/install-gbsd.svg',
    'src/image/logo.png',
    'src/image/disk.png',
    'src/image/laptop.png',
    'src/image/install.png',
    'src/image/installation.jpg'
]

data_files = [
    (f'{prefix}/lib/setup-station', ['src/ghostbsd-style.css']),
    (f'{prefix}/lib/setup-station/image', lib_setup_station_image),
    (f'{prefix}/share/applications', ['src/setup-station.desktop'])
]

# Add locale files if they exist
if os.path.exists('build/mo'):
    data_files.extend(data_file_list(f'{prefix}/share/locale', 'build/mo'))

setup(
    name="setup-station",
    version=PROGRAM_VERSION,
    description="Setup Station - GhostBSD post-installation setup utility",
    license='BSD',
    author='Eric Turgeon',
    url='https://github.com/GhostBSD/setup-station/',
    package_dir={'': '.'},
    install_requires=['setuptools'],
    packages=['setup_station'],
    scripts=['setup-station-init'],
    data_files=data_files,
    cmdclass={
            'create_translation': CreateTranslationCommand,
            'update_translations': UpdateTranslationsCommand,
            "build": build_extra,
            "build_i18n": build_i18n,
            "clean": clean_i18n
        }
)