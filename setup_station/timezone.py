"""
Timezone configuration module following the utility class pattern.
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import os
from setup_station.system_calls import timezone_dictionary
from setup_station.data import (
    SetupData,
    tmp,
    css_path,
    get_text
)
from setup_station.window import Window

tzdictionary = timezone_dictionary()

cssProvider = Gtk.CssProvider()
cssProvider.load_from_path(css_path)
screen = Gdk.Screen.get_default()
styleContext = Gtk.StyleContext()
styleContext.add_provider_for_screen(
    screen,
    cssProvider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


class TimeZone:
    """
    Utility class for the timezone selection screen following the utility class pattern.
    
    This class provides a GTK+ interface for timezone selection including:
    - Continent selection from available continents
    - City selection based on selected continent
    - Integration with SetupData for persistent configuration
    - Two-panel selection interface for easy navigation
    
    The class follows a utility pattern with class methods and variables for state management,
    designed to integrate with the main application for navigation flow.
    """
    # Class variables instead of instance variables
    vbox1: Gtk.Box | None = None
    continent: str | None = None
    city: str | None = None
    continenttreeView: Gtk.TreeView | None = None
    citytreeView: Gtk.TreeView | None = None
    city_store: Gtk.TreeStore | None = None
    continenttree_selection: Gtk.TreeSelection | None = None

    @classmethod
    def continent_columns(cls, treeView: Gtk.TreeView) -> None:
        """Setup the continent column in the tree view."""
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(None, cell, text=0)
        column_header = Gtk.Label(label='<b>' + get_text('Continent') + '</b>')
        column_header.set_use_markup(True)
        column_header.show()
        column.set_widget(column_header)
        column.set_sort_column_id(0)
        treeView.append_column(column)

    @classmethod
    def city_columns(cls, treeView: Gtk.TreeView) -> None:
        """Setup the city column in the tree view."""
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(None, cell, text=0)
        column_header = Gtk.Label(label='<b>' + get_text('City') + '</b>')
        column_header.set_use_markup(True)
        column_header.show()
        column.set_widget(column_header)
        column.set_sort_column_id(0)
        treeView.append_column(column)

    @classmethod
    def continent_selection(cls, tree_selection: Gtk.TreeSelection) -> None:
        """Handle continent selection from the tree view."""
        model, treeiter = tree_selection.get_selected()
        if cls.city_store:
            cls.city_store.clear()
        if treeiter is not None:
            value = model[treeiter][0]
            cls.continent = value
            if cls.city_store:
                for line in tzdictionary[cls.continent]:
                    cls.city_store.append(None, [line])
                if cls.citytreeView:
                    cls.citytreeView.set_cursor(0)

    @classmethod
    def city_selection(cls, tree_selection: Gtk.TreeSelection) -> None:
        """Handle city selection from the tree view."""
        model, treeiter = tree_selection.get_selected()
        if treeiter is not None:
            value = model[treeiter][0]
            cls.city = value
            # Save to SetupData
            if cls.continent and cls.city:
                SetupData.timezone = f'{cls.continent}/{cls.city}'

    @classmethod
    def apply_timezone(cls) -> None:
        """
        Apply timezone configuration to the system.

        Raises:
            ValueError: If no timezone selected or timezone is invalid
            RuntimeError: If timezone configuration fails
        """
        from setup_station.system_calls import set_timezone
        if not SetupData.timezone:
            raise ValueError("No timezone selected. Please select a continent and city.")
        set_timezone(SetupData.timezone)

    @classmethod
    def _initialize_ui(cls) -> None:
        """Initialize the user interface components."""
        cls.vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        cls.vbox1.show()
        
        box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)
        box2.set_border_width(10)
        cls.vbox1.pack_start(box2, True, True, 0)
        box2.show()
        
        table = Gtk.Table(1, 2, True)
        box2.pack_start(table, False, False, 0)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=10)
        hbox.set_border_width(5)
        box2.pack_start(hbox, True, True, 5)
        hbox.show()

        # Continent selection
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        store = Gtk.TreeStore(str)
        for line in tzdictionary:
            store.append(None, [line])
        cls.continenttreeView = Gtk.TreeView(store)
        cls.continenttreeView.set_model(store)
        cls.continenttreeView.set_rules_hint(True)
        cls.continent_columns(cls.continenttreeView)
        cls.continenttree_selection = cls.continenttreeView.get_selection()
        cls.continenttree_selection.set_mode(Gtk.SelectionMode.SINGLE)
        cls.continenttree_selection.connect("changed", cls.continent_selection)
        sw.add(cls.continenttreeView)
        sw.show()
        hbox.pack_start(sw, True, True, 5)

        # City selection
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        cls.city_store = Gtk.TreeStore(str)
        cls.citytreeView = Gtk.TreeView(cls.city_store)
        cls.citytreeView.set_model(cls.city_store)
        cls.citytreeView.set_rules_hint(True)
        cls.city_columns(cls.citytreeView)
        tree_selection = cls.citytreeView.get_selection()
        tree_selection.set_mode(Gtk.SelectionMode.SINGLE)
        tree_selection.connect("changed", cls.city_selection)
        sw.add(cls.citytreeView)
        sw.show()
        hbox.pack_start(sw, True, True, 5)

    @classmethod
    def get_model(cls) -> Gtk.Box:
        """Get the main widget for this screen."""
        if cls.vbox1 is None:
            cls._initialize_ui()
        if cls.continenttreeView:
            cls.continenttreeView.set_cursor(1)
        return cls.vbox1
