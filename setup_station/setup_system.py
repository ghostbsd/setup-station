import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
import threading
from time import sleep
from setup_station.language import Language
from setup_station.keyboard import Keyboard
from setup_station.timezone import TimeZone
from setup_station.add_admin import AddAdminUser
from setup_station.data import css_path, gif_logo

cssProvider = Gtk.CssProvider()
cssProvider.load_from_path(css_path)
screen = Gdk.Screen.get_default()
styleContext = Gtk.StyleContext()
styleContext.add_provider_for_screen(
    screen,
    cssProvider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


def update_progress(progress_bar: Gtk.ProgressBar, text: str) -> None:
    """
    This function is used to update the progress bar.
    :param progress_bar: The progress bar to update.
    :param text: The text to display.
    """
    new_val = progress_bar.get_fraction() + 0.000003
    progress_bar.set_fraction(new_val)
    progress_bar.set_text(text[0:80])


def setup_system(progress_bar: Gtk.ProgressBar) -> None:
    """
    This function is used to set up the system.
    :param progress_bar: The progress bar to update.
    """
    GLib.idle_add(update_progress, progress_bar, "Setting system language")
    Language.save_language()
    sleep(1)

    GLib.idle_add(update_progress, progress_bar, "Setting keyboard layout")
    Keyboard.save_keyboard()
    sleep(1)

    GLib.idle_add(update_progress, progress_bar, "Setting timezone")
    TimeZone.apply_timezone()
    sleep(1)

    GLib.idle_add(update_progress, progress_bar, "Creating admin user")
    AddAdminUser.save_admin_user()
    sleep(1)

    GLib.idle_add(update_progress, progress_bar, "Setup complete!")
    sleep(1)


class SetupWindow:

    def __init__(self) -> None:
        self.vBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        self.vBox.show()
        label = Gtk.Label(label="Getting everything ready", name="Header")
        label.set_property("height-request", 50)
        self.vBox.pack_start(label, False, False, 0)

        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=0, name="install")
        h_box.show()
        self.vBox.pack_end(h_box, True, True, 0)
        v_box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        v_box2.show()
        label2 = Gtk.Label(name="sideText")

        label2.set_markup(
            "This should not take too long.\n\n"
            "Don't turn your system off."
        )
        label2.set_justify(Gtk.Justification.LEFT)
        label2.set_line_wrap(True)
        # label2.set_max_width_chars(10)
        label2.set_alignment(0.5, 0.4)
        h_box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=0, name="TransBox")
        h_box2.show()
        h_box.pack_start(h_box2, True, True, 0)
        h_box2.pack_start(label2, True, True, 0)

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
