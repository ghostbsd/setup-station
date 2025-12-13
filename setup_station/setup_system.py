import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
import threading
from time import sleep
from setup_station.data import css_path, gif_logo, get_text

cssProvider = Gtk.CssProvider()
cssProvider.load_from_path(css_path)
screen = Gdk.Screen.get_default()
styleContext = Gtk.StyleContext()
styleContext.add_provider_for_screen(
    screen,
    cssProvider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


def update_progress(progress_bar: Gtk.ProgressBar, fraction: float, text: str) -> None:
    """
    Update the progress bar with a specific fraction and text.

    :param progress_bar: The progress bar to update.
    :param fraction: Progress fraction (0.0 to 1.0)
    :param text: The text to display.
    """
    progress_bar.set_fraction(fraction)
    progress_bar.set_text(text)


def setup_system(progress_bar: Gtk.ProgressBar) -> None:
    """
    This function is used to set up the system.
    :param progress_bar: The progress bar to update.
    """
    from setup_station.language import Language
    from setup_station.keyboard import Keyboard
    from setup_station.timezone import TimeZone
    from setup_station.add_admin import AddAdminUser
    from setup_station.system_calls import (
        enable_lightdm,
        remove_ghostbsd_autologin,
        start_lightdm
    )

    # Step 0/6: Setting system language
    GLib.idle_add(update_progress, progress_bar, 0/6, get_text("Setting system language"))
    Language.save_language()
    sleep(1)

    # Step 1/6: Setting keyboard layout
    GLib.idle_add(update_progress, progress_bar, 1/6, get_text("Setting keyboard layout"))
    Keyboard.save_keyboard()
    sleep(1)

    # Step 2/6: Setting timezone
    GLib.idle_add(update_progress, progress_bar, 2/6, get_text("Setting timezone"))
    TimeZone.apply_timezone()
    sleep(1)

    # Step 3/6: Creating admin user
    GLib.idle_add(update_progress, progress_bar, 3/6, get_text("Creating admin user"))
    AddAdminUser.save_admin_user()
    sleep(1)

    # Step 4/6: Enabling display manager
    GLib.idle_add(update_progress, progress_bar, 4/6, get_text("Enabling display manager"))
    enable_lightdm()
    sleep(1)

    # Step 5/6: Removing system setup autologin
    GLib.idle_add(update_progress, progress_bar, 5/6, get_text("Removing system setup autologin"))
    remove_ghostbsd_autologin()
    sleep(1)

    # Step 6/6: Setup complete
    GLib.idle_add(update_progress, progress_bar, 1, get_text("Setup complete!"))
    sleep(1)

    # Update label text before starting lightdm
    def update_label():
        SetupWindow.slide_text.set_markup(
            get_text("Configuration complete.") +
            "\n\n" +
            get_text("Starting the login screen...")
        )

    GLib.idle_add(update_label)
    sleep(2)

    # Start lightdm and exit
    start_lightdm()

    import sys
    sys.exit(0)


class SetupWindow:
    slide_text: Gtk.Label | None = None

    def __init__(self) -> None:
        self.vBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        self.vBox.show()
        label = Gtk.Label(label=get_text("Getting everything ready"), name="Header")
        label.set_property("height-request", 50)
        self.vBox.pack_start(label, False, False, 0)

        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=0, name="install")
        h_box.show()
        self.vBox.pack_end(h_box, True, True, 0)
        v_box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        v_box2.show()
        SetupWindow.slide_text = Gtk.Label(name="sideText")

        SetupWindow.slide_text.set_markup(
            get_text("Setting up your system.") +
            "\n\n" +
            get_text("Please do not turn off your computer.")
        )
        SetupWindow.slide_text.set_justify(Gtk.Justification.LEFT)
        SetupWindow.slide_text.set_line_wrap(True)
        # SetupWindow.slide_text.set_max_width_chars(10)
        SetupWindow.slide_text.set_alignment(0.5, 0.4)
        SetupWindow.slide_text.show()
        h_box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=0, name="TransBox")
        h_box2.show()
        h_box.pack_start(h_box2, True, True, 0)
        h_box2.pack_start(SetupWindow.slide_text, True, True, 0)

        image = Gtk.Image()
        image.set_from_file(gif_logo)
        # image.set_size_request(width=256, height=256)
        image.show()
        h_box.pack_end(image, True, True, 20)

    def get_model(self) -> Gtk.Box:
        return self.vBox


class SetupProgress:

    def __init__(self) -> None:
        self.pbar = Gtk.ProgressBar()
        self.pbar.set_show_text(True)
        thr = threading.Thread(
            target=setup_system,
            args=(self.pbar,),
            daemon=True
        )
        thr.start()
        self.pbar.show()

    def get_progressbar(self) -> Gtk.ProgressBar:
        return self.pbar
