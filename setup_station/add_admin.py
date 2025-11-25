"""
This module is used to add the admin user following the utility class pattern.
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from setup_station.data import (
    SetupData,
    css_path
)
from setup_station.common import (
    password_strength,
)
from setup_station.system_calls import set_admin_user

cssProvider = Gtk.CssProvider()
cssProvider.load_from_path(css_path)
screen = Gdk.Screen.get_default()
styleContext = Gtk.StyleContext()
styleContext.add_provider_for_screen(
    screen,
    cssProvider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


class AddAdminUser:
    """
    Utility class for the admin user setup screen following the utility class pattern.
    
    This class provides a GTK+ interface for admin user creation including:
    - Username and full name entry
    - Password entry with strength validation
    - Shell selection
    - Integration with SetupData for persistent configuration
    - Root password setting (same as user password)
    
    The class follows a utility pattern with class methods and variables for state management,
    designed to integrate with the main application for navigation flow.
    """
    # Class variables instead of instance variables
    vbox1: Gtk.Box | None = None
    user: Gtk.Entry | None = None
    name: Gtk.Entry | None = None
    password: Gtk.Entry | None = None
    repassword: Gtk.Entry | None = None
    label3: Gtk.Label | None = None
    img: Gtk.Image | None = None
    host: Gtk.Entry | None = None
    shell: str = '/usr/local/bin/fish'

    @classmethod
    def save_user_data(cls) -> None:
        """Save user data to SetupData."""
        # Validate all widgets exist before accessing
        if not all([cls.user, cls.name, cls.password, cls.host]):
            raise ValueError("UI widgets not initialized")

        # Get values from widgets
        username = cls.user.get_text()
        fullname = cls.name.get_text()
        password = cls.password.get_text()
        hostname = cls.host.get_text()

        # Basic validation - just check not empty
        if not username:
            raise ValueError("Username is required")
        if not fullname:
            raise ValueError("Full name is required")
        if not password:
            raise ValueError("Password is required")

        # Save to SetupData
        SetupData.username = username
        SetupData.user_fullname = fullname
        SetupData.user_password = password
        SetupData.user_shell = cls.shell
        SetupData.user_home_directory = f'/home/{username}'
        SetupData.hostname = hostname if hostname else f'{username}-ghostbsd'
        SetupData.root_password = password

    @classmethod
    def get_user_information(cls) -> dict:
        """Get current user information as a dictionary."""
        return {
            'username': SetupData.username,
            'name': SetupData.user_fullname,
            'password': SetupData.user_password,
            'shell': SetupData.user_shell,
            'home_directory': SetupData.user_home_directory,
            'hostname': SetupData.hostname
        }

    @classmethod
    def save_admin_user(cls) -> None:
        """
        Save admin user configuration and apply system changes.

        Raises:
            ValueError: If user data validation fails
            subprocess.CalledProcessError: If system commands fail
        """
        cls.save_user_data()
        set_admin_user(
            SetupData.username,
            SetupData.user_fullname,
            SetupData.user_password,
            SetupData.user_shell,
            SetupData.user_home_directory,
            SetupData.hostname
        )

    @classmethod
    def on_shell(cls, widget: Gtk.ComboBoxText) -> None:
        """Handle shell selection changes."""
        shell = widget.get_active_text()
        if shell == 'sh':
            cls.shell = '/bin/sh'
        elif shell == 'csh':
            cls.shell = '/bin/csh'
        elif shell == 'tcsh':
            cls.shell = '/bin/tcsh'
        elif shell == 'fish':
            cls.shell = '/usr/local/bin/fish'
        elif shell == 'bash':
            cls.shell = '/usr/local/bin/bash'
        elif shell == 'rbash':
            cls.shell = '/usr/local/bin/rbash'
        elif shell == 'zsh':
            cls.shell = '/usr/local/bin/zsh'
        elif shell == 'ksh':
            cls.shell = '/usr/local/bin/ksh93'

    @classmethod
    def user_and_host(cls, _widget: Gtk.Entry) -> None:
        """Auto-generate username and hostname from full name."""
        if cls.name and cls.user and cls.host:
            username = cls.name.get_text().split()
            if len(username) > 0:
                cls.host.set_text(f"{username[0].lower()}-ghostbsd-pc")
                cls.user.set_text(username[0].lower())
            else:
                cls.host.set_text("")
                cls.user.set_text("")

    @classmethod
    def _initialize_ui(cls) -> None:
        """Initialize the user interface components."""
        cls.vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        cls.vbox1.show()
        admin_message = Gtk.Label(label="The initial root password will be set to the admin user password.")
        cls.vbox1.pack_start(admin_message, False, False, 0)
        
        box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        box2.set_border_width(10)
        cls.vbox1.pack_start(box2, False, False, 0)
        box2.show()
        
        box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)
        cls.vbox1.pack_start(box2, False, False, 0)
        box2.show()
        
        label = Gtk.Label(label='<b>User Account</b>')
        label.set_use_markup(True)
        label.set_alignment(.2, .2)
        
        username_label = Gtk.Label(label="User name")
        cls.user = Gtk.Entry()
        name_label = Gtk.Label(label="Real name")
        cls.name = Gtk.Entry()
        cls.name.connect("changed", cls.user_and_host)
        
        password_label = Gtk.Label(label="Password")
        cls.password = Gtk.Entry()
        cls.password.set_visibility(False)
        cls.password.connect("changed", cls.password_verification)
        
        verify_label = Gtk.Label(label="Verify Password")
        cls.repassword = Gtk.Entry()
        cls.repassword.set_visibility(False)
        cls.repassword.connect("changed", cls.password_verification)
        
        shell_label = Gtk.Label(label="Shell")
        shell = Gtk.ComboBoxText()
        shell.append_text('sh')
        shell.append_text('csh')
        shell.append_text('tcsh')
        shell.append_text('fish')
        shell.append_text('bash')
        shell.append_text('rbash')
        shell.append_text('ksh')
        shell.append_text('zsh')
        shell.set_active(3)  # Default to fish
        shell.connect("changed", cls.on_shell)
        
        hostname_label = Gtk.Label(label='<b>Set Hostname</b>')
        hostname_label.set_use_markup(True)
        hostname_label.set_alignment(0, .5)
        cls.host = Gtk.Entry()
        
        table = Gtk.Table(1, 3, True)
        table.set_row_spacings(10)
        table.attach(name_label, 0, 1, 1, 2)
        table.attach(cls.name, 1, 2, 1, 2)
        table.attach(username_label, 0, 1, 2, 3)
        table.attach(cls.user, 1, 2, 2, 3)
        table.attach(password_label, 0, 1, 4, 5)
        table.attach(cls.password, 1, 2, 4, 5)
        
        cls.label3 = Gtk.Label()
        table.attach(cls.label3, 2, 3, 4, 5)
        table.attach(verify_label, 0, 1, 5, 6)
        table.attach(cls.repassword, 1, 2, 5, 6)
        
        # Set image for password matching
        cls.img = Gtk.Image()
        table.attach(cls.img, 2, 3, 5, 6)
        
        box2.pack_start(table, False, False, 0)
        
        box3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)
        box3.set_border_width(10)
        cls.vbox1.pack_start(box3, True, True, 0)
        box3.show()

    @classmethod
    def get_model(cls) -> Gtk.Box:
        """Get the main widget for this screen."""
        if cls.vbox1 is None:
            cls._initialize_ui()
        return cls.vbox1

    @classmethod
    def password_verification(cls, _widget: Gtk.Entry) -> None:
        """Verify password matches and check strength."""
        if cls.password and cls.repassword and cls.label3 and cls.img:
            password = cls.password.get_text()
            repassword = cls.repassword.get_text()

            # Get password strength message and display it
            strength_message = password_strength(password)
            cls.label3.set_text(strength_message)

            # Check if passwords match, meet requirements, and are allowed
            passwords_match = password == repassword and password != "" and " " not in password
            password_allowed = strength_message not in ["Password not allowed", "Space not allowed"]

            if passwords_match and password_allowed:
                cls.img.set_from_stock(Gtk.STOCK_YES, 5)
                # Enable next button logic would go here
            else:
                cls.img.set_from_stock(Gtk.STOCK_NO, 5)
                # Disable next button logic would go here


# Backward compatibility alias
AddUser = AddAdminUser
