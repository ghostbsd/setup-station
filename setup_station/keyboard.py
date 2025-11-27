"""
Keyboard configuration module following the utility class pattern.
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from setup_station.system_calls import (
    keyboard_dictionary,
    keyboard_models,
    change_keyboard,
    set_keyboard
)
from setup_station.data import (
    SetupData,
    css_path,
    get_text
)

kb_dictionary = keyboard_dictionary()
kbm_dictionary = keyboard_models()

cssProvider = Gtk.CssProvider()
cssProvider.load_from_path(css_path)
screen = Gdk.Screen.get_default()
styleContext = Gtk.StyleContext()
styleContext.add_provider_for_screen(
    screen,
    cssProvider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


# This class is for placeholder for entry.
class PlaceHolderEntry(Gtk.Entry):

    placeholder = 'Type here to test your keyboard'
    _default = True

    def __init__(self, *args, **kwds):
        Gtk.Entry.__init__(self, *args, **kwds)
        self.placeholder = get_text('Type here to test your keyboard')
        self.set_text(self.placeholder)
        # self.modify_text(Gtk.STATE_NORMAL, Gtk.gdk.color_parse("#4d4d4d"))
        self._default = True
        self.connect('focus-in-event', self._focus_in_event)
        self.connect('focus-out-event', self._focus_out_event)

    def _focus_in_event(self, _widget, _event):
        if self._default:
            self.set_text('')
            # self.modify_text(Gtk.STATE_NORMAL, Gtk.gdk.color_parse('black'))

    def _focus_out_event(self, _widget, _event):
        if Gtk.Entry.get_text(self) == '':
            self.set_text(self.placeholder)
            # self.modify_text(Gtk.STATE_NORMAL,
            #                    Gtk.gdk.color_parse("#4d4d4d"))
            self._default = True
        else:
            self._default = False

    def get_text(self):
        if self._default:
            return ''
        return Gtk.Entry.get_text(self)


class Keyboard:
    """
    Utility class for the keyboard configuration screen following the utility class pattern.
    
    This class provides a GTK+ interface for keyboard configuration including:
    - Keyboard layout selection from available system layouts
    - Keyboard model selection
    - Live keyboard testing with placeholder entry
    - Integration with SetupData for persistent configuration
    - Real-time keyboard switching for immediate testing
    
    The class follows a utility pattern with class methods and variables for state management,
    designed to integrate with the main application for navigation flow.
    """
    # Class variables instead of instance variables
    vbox1: Gtk.Box | None = None
    kb_layout: str | None = None
    kb_variant: str | None = None
    kb_model: str | None = None
    treeView: Gtk.TreeView | None = None
    model_store: Gtk.TreeStore | None = None
    tree_selection: Gtk.TreeSelection | None = None

    @classmethod
    def layout_columns(cls, treeview: Gtk.TreeView) -> None:
        """Setup the keyboard layout column in the tree view."""
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(None, cell, text=0)
        column_header = Gtk.Label(label='<b>' + get_text('Keyboard Layout') + '</b>')
        column_header.set_use_markup(True)
        column_header.show()
        column.set_widget(column_header)
        column.set_sort_column_id(0)
        treeview.append_column(column)

    @classmethod
    def variant_columns(cls, treeview: Gtk.TreeView) -> None:
        """Setup the keyboard model column in the tree view."""
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(None, cell, text=0)
        column_header = Gtk.Label(label='<b>' + get_text('Keyboard Models') + '</b>')
        column_header.set_use_markup(True)
        column_header.show()
        column.set_widget(column_header)
        column.set_sort_column_id(0)
        treeview.append_column(column)

    @classmethod
    def layout_selection(cls, tree_selection: Gtk.TreeSelection) -> None:
        """Handle keyboard layout selection from the tree view."""
        model, treeiter = tree_selection.get_selected()
        if treeiter is not None:
            value = model[treeiter][0]
            kb_lv = kb_dictionary[value]
            cls.kb_layout = kb_lv['layout']
            cls.kb_variant = kb_lv['variant']
            try:
                change_keyboard(cls.kb_layout, cls.kb_variant)
            except RuntimeError as e:
                print(f"Warning: Failed to apply keyboard layout immediately: {e}")
            # Save to SetupData
            SetupData.keyboard_layout = cls.kb_layout
            SetupData.keyboard_variant = cls.kb_variant or ""

    @classmethod
    def model_selection(cls, tree_selection: Gtk.TreeSelection) -> None:
        """Handle keyboard model selection from the tree view."""
        model, treeiter = tree_selection.get_selected()
        if treeiter is not None:
            value = model[treeiter][0]
            cls.kb_model = kbm_dictionary[value]
            try:
                change_keyboard(cls.kb_layout, cls.kb_variant, cls.kb_model)
            except RuntimeError as e:
                print(f"Warning: Failed to apply keyboard model immediately: {e}")
            # Save to SetupData
            SetupData.keyboard_model = cls.kb_model

    @classmethod
    def get_model(cls) -> Gtk.Box:
        """Get the main widget for this screen."""
        if cls.vbox1 is None:
            cls._initialize_ui()
        if cls.treeView:
            cls.treeView.set_cursor(0)
        return cls.vbox1

    @classmethod
    def save_keyboard_data(cls) -> None:
        """Save keyboard data to SetupData."""
        SetupData.keyboard_layout = cls.kb_layout or ""
        SetupData.keyboard_variant = cls.kb_variant or ""
        SetupData.keyboard_model = cls.kb_model or ""

    @classmethod
    def save_keyboard(cls) -> None:
        """
        Apply keyboard configuration to the system.

        Raises:
            IOError: If file operations fail
            RuntimeError: If keyboard configuration fails
        """
        cls.save_keyboard_data()
        set_keyboard(
            SetupData.keyboard_layout,
            SetupData.keyboard_variant,
            SetupData.keyboard_model
        )

    @classmethod
    def _initialize_ui(cls) -> None:
        """Initialize the user interface components."""
        cls.vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        cls.vbox1.show()
        vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)
        vbox2.set_border_width(10)
        cls.vbox1.pack_start(vbox2, True, True, 0)
        vbox2.show()
        table = Gtk.Table(1, 2, True)
        vbox2.pack_start(table, False, False, 0)
        hbox1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=10)
        hbox1.set_border_width(5)
        vbox2.pack_start(hbox1, True, True, 5)
        hbox1.show()

        # Keyboard layout selection
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        store = Gtk.TreeStore(str)
        store.append(None, ['English (US)'])
        store.append(None, ['English (Canada)'])
        store.append(None, ['French (Canada)'])
        for line in sorted(kb_dictionary):
            store.append(None, [line.rstrip()])
        cls.treeView = Gtk.TreeView()
        cls.treeView.set_model(store)
        cls.treeView.set_rules_hint(True)
        cls.layout_columns(cls.treeView)
        cls.tree_selection = cls.treeView.get_selection()
        cls.tree_selection.set_mode(Gtk.SelectionMode.SINGLE)
        cls.tree_selection.connect("changed", cls.layout_selection)
        sw.add(cls.treeView)
        sw.show()
        hbox1.pack_start(sw, True, True, 5)

        # Keyboard model selection
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        cls.model_store = Gtk.TreeStore(str)
        for line in sorted(kbm_dictionary):
            cls.model_store.append(None, [line.rstrip()])
        treeview = Gtk.TreeView()
        treeview.set_model(cls.model_store)
        treeview.set_rules_hint(True)
        cls.variant_columns(treeview)
        tree_selection = treeview.get_selection()
        tree_selection.set_mode(Gtk.SelectionMode.SINGLE)
        tree_selection.connect("changed", cls.model_selection)
        sw.add(treeview)
        sw.show()
        hbox1.pack_start(sw, True, True, 5)

        # Keyboard testing area
        vbox3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=10)
        vbox3.set_border_width(5)
        cls.vbox1.pack_start(vbox3, False, False, 0)
        vbox3.show()
        vbox3.pack_start(PlaceHolderEntry(), True, True, 10)
