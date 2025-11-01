"""
Interface Controller Module.

This module provides the main navigation interface and button controls
for the Setup Station GTK application wizard.
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from setup_station.setup_system import SetupWindow, SetupProgress
from setup_station.window import Window
from setup_station.data import SetupData, get_text
import os
import shutil


class Button:
    """
    Button management class for navigation controls.
    
    Manages the Back and Next buttons used throughout
    the setup wizard interface.
    """
    back_button: Gtk.Button = Gtk.Button(label=get_text('Back'))
    """This button is used to go back to the previous page."""
    next_button: Gtk.Button = Gtk.Button(label=get_text('Next'))
    """This button is used to go to the next page."""
    _box: Gtk.Box | None = None

    @classmethod
    def update_button_labels(cls) -> None:
        """Update button labels with current language translations."""
        cls.back_button.set_label(get_text('Back'))
        cls.next_button.set_label(get_text('Next'))

    @classmethod
    def hide_all(cls) -> None:
        """
        This method hides all buttons.
        """
        cls.back_button.hide()
        cls.next_button.hide()

    @classmethod
    def show_initial(cls) -> None:
        """
        This method shows the initial buttons. Just Next.
        """
        cls.back_button.hide()
        cls.next_button.show()

    @classmethod
    def show_back(cls) -> None:
        """
        This method shows the back button.
        """
        cls.back_button.show()

    @classmethod
    def hide_back(cls) -> None:
        """
        This method hides the back button.
        """
        cls.back_button.hide()

    @classmethod
    def box(cls) -> Gtk.Box:
        """
        This method creates a box container of buttons aligned to the right.

        Returns:
            Box container with buttons aligned to the right for navigation.
        """
        if cls._box is None:
            # Use Box for better right-alignment control
            cls._box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=5)
            cls._box.set_halign(Gtk.Align.END)  # Align the entire box to the right
            
            cls.back_button.connect("clicked", Interface.back_page)
            cls._box.pack_start(cls.back_button, False, False, 0)
            
            cls.next_button.connect("clicked", Interface.next_page)
            cls._box.pack_start(cls.next_button, False, False, 0)
            
            cls._box.show()
        return cls._box


class Interface:
    """
    Main interface controller for the setup wizard.
    
    Manages the GTK Notebook pages and navigation between different
    screens in the setup process including language, keyboard,
    timezone, network setup, and admin user configuration.
    """
    language = None
    keyboard = None
    timezone = None
    network_setup = None
    add_admin = None
    page: Gtk.Notebook = Gtk.Notebook()
    nbButton: Gtk.Notebook | None = None

    @classmethod
    def get_interface(cls) -> Gtk.Box:
        interface_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        interface_box.show()
        interface_box.pack_start(cls.page, True, True, 0)
        cls.page.show()
        cls.page.set_show_tabs(False)
        cls.page.set_show_border(False)
        
        # Create the language page
        language_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        language_box.show()
        cls.language.initialize()
        get_types = cls.language.get_model()
        language_box.pack_start(get_types, True, True, 0)
        Window.set_title(get_text("GhostBSD Initial Setup"))
        label = Gtk.Label(label=get_text("Language"))
        cls.page.insert_page(language_box, label, 0)
        
        # Set what page to start at
        cls.page.set_current_page(0)
        
        # Create button container
        cls.nbButton = Gtk.Notebook()
        interface_box.pack_end(cls.nbButton, False, False, 5)
        cls.nbButton.show()
        cls.nbButton.set_show_tabs(False)
        cls.nbButton.set_show_border(False)
        label = Gtk.Label(label=get_text("Button"))
        cls.nbButton.insert_page(Button.box(), label, 0)
        
        return interface_box

    @classmethod
    def delete(cls, _widget: Gtk.Widget, _event=None) -> None:
        """Close the main window."""
        if os.path.exists('/tmp/.setup-station'):
            shutil.rmtree('/tmp/.setup-station')
        SetupData.reset()
        Gtk.main_quit()

    @classmethod
    def next_page(cls, _widget: Gtk.Button) -> None:
        """Go to the next window."""
        page = cls.page.get_current_page()
        if page == 0:
            # Check if the keyboard page already exists
            if cls.page.get_n_pages() <= 1:
                keyboard_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
                keyboard_box.show()
                get_keyboard = cls.keyboard.get_model()
                keyboard_box.pack_start(get_keyboard, True, True, 0)
                label = Gtk.Label(label=get_text("Keyboard"))
                cls.page.insert_page(keyboard_box, label, 1)
            cls.page.next_page()
            Window.show_all()
            Button.show_back()
            Button.next_button.set_sensitive(True)
        elif page == 1:
            # Check if the timezone page already exists
            if cls.page.get_n_pages() <= 2:
                timezone_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
                timezone_box.show()
                get_timezone = cls.timezone.get_model()
                timezone_box.pack_start(get_timezone, True, True, 0)
                label = Gtk.Label(label=get_text("Time Zone"))
                cls.page.insert_page(timezone_box, label, 2)
            cls.page.next_page()
            Window.show_all()
            Button.next_button.set_sensitive(True)
        elif page == 2:
            # Check if the network setup page already exists
            if cls.page.get_n_pages() <= 3:
                network_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
                network_box.show()
                get_network = cls.network_setup.get_model()
                network_box.pack_start(get_network, True, True, 0)
                label = Gtk.Label(label=get_text("Network"))
                cls.page.insert_page(network_box, label, 3)
            cls.page.next_page()
            Window.show_all()
            Button.next_button.set_sensitive(True)
        elif page == 3:
            # Check if the admin user page already exists
            if cls.page.get_n_pages() <= 4:
                admin_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
                admin_box.show()
                get_admin = cls.add_admin.get_model()
                admin_box.pack_start(get_admin, True, True, 0)
                label = Gtk.Label(label=get_text("Admin User"))
                cls.page.insert_page(admin_box, label, 4)
            cls.page.next_page()
            Window.show_all()
            Button.next_button.set_sensitive(False)
        elif page == 4:
            # Create the Setup Progress page
            install_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
            install_box.show()
            install = SetupWindow()
            get_install = install.get_model()
            install_box.pack_start(get_install, True, True, 0)
            label = Gtk.Label(label=get_text("Setup GhostBSD"))
            cls.page.insert_page(install_box, label, 5)
            cls.page.next_page()
            
            # Start the setup progress
            instpro = SetupProgress()
            progress_bar = instpro.get_progressbar()
            box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
            box1.show()
            label = Gtk.Label(label=get_text("Progress Bar"))
            box1.pack_end(progress_bar, False, False, 0)
            cls.nbButton.insert_page(box1, label, 1)
            cls.nbButton.next_page()
            Window.show_all()
            
        # Update window title
        current_page_widget = cls.page.get_nth_page(cls.page.get_current_page())
        title_text = cls.page.get_tab_label_text(current_page_widget)
        Window.set_title(title_text)

    @classmethod
    def back_page(cls, _widget: Gtk.Button) -> None:
        """Go back to the previous window."""
        current_page = cls.page.get_current_page()
        if current_page == 1:
            # Going back to the language page hide back button
            Button.hide_back()
        cls.page.prev_page()
        
        # Update window title
        current_page_widget = cls.page.get_nth_page(cls.page.get_current_page())
        title_text = cls.page.get_tab_label_text(current_page_widget)
        Window.set_title(title_text)