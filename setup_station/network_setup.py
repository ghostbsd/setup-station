"""
Network setup module following the utility class pattern.
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import re
import threading
from time import sleep
from NetworkMgr.net_api import (
    network_dictionary,
    scan_networks,
    request_scan,
    wait_for_daemon,
    connect_to_ssid,
    wait_for_connection,
    enable_all_networks,
    wpa_reconfigure,
    wpa_save_config,
    ssid_is_saved,
    save_psk_network,
    update_psk_network,
    save_open_network
)
from setup_station.data import css_path, get_text

cssProvider = Gtk.CssProvider()
cssProvider.load_from_path(css_path)
screen = Gdk.Screen.get_default()
styleContext = Gtk.StyleContext()
styleContext.add_provider_for_screen(
    screen,
    cssProvider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

# wpa_cli scan returns at once, the results land a few seconds later.
SCAN_WAIT = 4


class NetworkSetup:
    """
    Utility class for network setup screen following the utility class pattern.

    Provides interface for detecting and configuring wired and wireless network connections.
    """
    # Class variables for UI state
    vbox1: Gtk.Box | None = None
    network_info: dict | None = None
    networks: dict = {}
    wire_connection_label: Gtk.Label | None = None
    wire_connection_image: Gtk.Image | None = None
    wifi_connection_label: Gtk.Label | None = None
    wifi_connection_image: Gtk.Image | None = None
    connection_box: Gtk.Box | None = None
    store: Gtk.ListStore | None = None
    window: Gtk.Window | None = None
    password: Gtk.Entry | None = None

    @classmethod
    def get_model(cls) -> Gtk.Box:
        """
        Return the GTK widget model for the network setup interface.

        Uses lazy initialization - creates UI on first call.

        Returns:
            Gtk.Box: The main container widget for the network setup interface
        """
        if cls.vbox1 is None:
            cls.initialize()
        return cls.vbox1

    @staticmethod
    def wifi_stat(bar: int) -> str:
        """
        Convert WiFi signal strength to icon name.

        Args:
            bar: Signal strength percentage

        Returns:
            str: Icon name for the signal strength
        """
        if bar > 75:
            return 'nm-signal-100'
        elif bar > 50:
            return 'nm-signal-75'
        elif bar > 25:
            return 'nm-signal-50'
        elif bar > 5:
            return 'nm-signal-25'
        else:
            return 'nm-signal-00'

    @classmethod
    def update_network_detection(cls) -> None:
        """
        Update the network connection status display.

        Checks wired and wireless connections and updates the UI accordingly.
        """
        cards = cls.network_info['cards']
        card_list = list(cards.keys())
        r = re.compile("wlan")
        wlan_list = list(filter(r.match, card_list))
        wire_list = list(set(card_list).difference(wlan_list))
        cards = cls.network_info['cards']
        if wire_list:
            for card in wire_list:
                if cards[card]['state']['connection'] == 'Connected':

                    wire_text = get_text('Network card connected to the internet')
                    cls.wire_connection_image.set_from_stock(Gtk.STOCK_YES, 5)
                    print('Connected True')
                    break
            else:
                wire_text = get_text('Network card not connected to the internet')
                cls.wire_connection_image.set_from_stock(Gtk.STOCK_NO, 5)
        else:
            wire_text = get_text('No network card detected')
            cls.wire_connection_image.set_from_stock(Gtk.STOCK_NO, 5)

        cls.wire_connection_label.set_label(wire_text)

        if wlan_list:
            for wlan_card in wlan_list:
                if cards[wlan_card]['state']['connection'] == 'Connected':
                    wifi_text = get_text('WiFi card detected and connected to an access point')
                    cls.wifi_connection_image.set_from_stock(Gtk.STOCK_YES, 5)
                    break
            else:
                wifi_text = get_text('WiFi card detected but not connected to an access point')
                cls.wifi_connection_image.set_from_stock(Gtk.STOCK_NO, 5)
        else:
            wifi_text = get_text("WiFi card not detected or not supported")
            cls.wifi_connection_image.set_from_stock(Gtk.STOCK_NO, 5)

        cls.wifi_connection_label.set_label(wifi_text)

    @classmethod
    def initialize(cls) -> None:
        """
        Initialize the network setup UI.

        Detects network interfaces and creates the interface for wired/wireless setup.
        """
        cls.network_info = network_dictionary()
        print(cls.network_info)
        cls.vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        cls.vbox1.show()
        cards = cls.network_info['cards']
        card_list = list(cards.keys())
        r = re.compile("wlan")
        wlan_list = list(filter(r.match, card_list))
        wire_list = list(set(card_list).difference(wlan_list))

        cls.wire_connection_label = Gtk.Label()
        cls.wire_connection_label.set_xalign(0.01)
        cls.wire_connection_image = Gtk.Image()
        cls.wifi_connection_label = Gtk.Label()
        cls.wifi_connection_label.set_xalign(0.01)
        cls.wifi_connection_image = Gtk.Image()

        if wire_list:
            for card in wire_list:
                if cards[card]['state']['connection'] == 'Connected':
                    wire_text = get_text('Network card connected to the internet')
                    cls.wire_connection_image.set_from_stock(Gtk.STOCK_YES, 5)
                    print('Connected True')
                    break
            else:
                wire_text = get_text('Network card not connected to the internet')
                cls.wire_connection_image.set_from_stock(Gtk.STOCK_NO, 5)
        else:
            wire_text = get_text('No network card detected')
            cls.wire_connection_image.set_from_stock(Gtk.STOCK_NO, 5)

        cls.wire_connection_label.set_label(wire_text)
        wlan_card = ""
        if wlan_list:
            for wlan_card in wlan_list:
                if cards[wlan_card]['state']['connection'] == 'Connected':
                    wifi_text = get_text('WiFi card detected and connected to an access point')
                    cls.wifi_connection_image.set_from_stock(Gtk.STOCK_YES, 5)
                    break
            else:
                wifi_text = get_text('WiFi card detected but not connected to an access point')
                cls.wifi_connection_image.set_from_stock(Gtk.STOCK_NO, 5)
        else:
            wifi_text = get_text('WiFi card not detected or not supported')
            cls.wifi_connection_image.set_from_stock(Gtk.STOCK_NO, 5)

        cls.wifi_connection_label.set_label(wifi_text)

        cls.connection_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=True, spacing=20)
        if wlan_card:
            # add a default card variable
            sw = Gtk.ScrolledWindow()
            sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
            sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            cls.store = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str)
            cls.networks = scan_networks(wlan_card)
            cls.populate_ssid_list()
            threading.Thread(target=cls.scan_and_refresh, args=(wlan_card,), daemon=True).start()
            treeview = Gtk.TreeView()
            treeview.set_model(cls.store)
            treeview.set_rules_hint(True)
            pixbuf_cell = Gtk.CellRendererPixbuf()
            pixbuf_column = Gtk.TreeViewColumn(get_text('Stat'), pixbuf_cell)
            pixbuf_column.add_attribute(pixbuf_cell, "pixbuf", 0)
            pixbuf_column.set_resizable(True)
            treeview.append_column(pixbuf_column)
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(get_text('SSID'), cell, text=1)
            column.set_sort_column_id(1)
            treeview.append_column(column)
            tree_selection = treeview.get_selection()
            tree_selection.set_mode(Gtk.SelectionMode.SINGLE)
            tree_selection.connect("changed", cls.wifi_setup, wlan_card)
            sw.add(treeview)
            cls.connection_box.pack_start(sw, True, True, 50)

        main_grid = Gtk.Grid()
        main_grid.set_row_spacing(10)
        main_grid.set_column_spacing(10)
        main_grid.set_column_homogeneous(True)
        main_grid.set_row_homogeneous(True)
        cls.vbox1.pack_start(main_grid, True, True, 10)
        main_grid.attach(cls.wire_connection_image, 2, 1, 1, 1)
        main_grid.attach(cls.wire_connection_label, 3, 1, 8, 1)
        main_grid.attach(cls.wifi_connection_image, 2, 2, 1, 1)
        main_grid.attach(cls.wifi_connection_label, 3, 2, 8, 1)
        main_grid.attach(cls.connection_box, 1, 4, 10, 5)

    @classmethod
    def populate_ssid_list(cls) -> None:
        """Fill the access point list from the latest scan of the WiFi card."""
        cls.store.clear()
        for ssid, network in cls.networks.items():
            stat = NetworkSetup.wifi_stat(network['signal'])
            pixbuf = Gtk.IconTheme.get_default().load_icon(stat, 32, 0)
            cls.store.append([pixbuf, ssid, network['security']])

    @classmethod
    def scan_and_refresh(cls, wifi_card: str) -> None:
        """
        Scan the WiFi card and hand the results to the UI thread.

        The card may have an empty or stale scan table when the page opens.

        Args:
            wifi_card: Name of the wireless network interface
        """
        if wait_for_daemon(wifi_card) and request_scan(wifi_card):
            sleep(SCAN_WAIT)
        GLib.idle_add(cls.refresh_networks, scan_networks(wifi_card))

    @classmethod
    def refresh_networks(cls, networks: dict) -> None:
        """
        Show a new scan of the access points.

        Args:
            networks: Access points returned by scan_networks()
        """
        cls.networks = networks
        cls.populate_ssid_list()

    @classmethod
    def wifi_setup(cls, tree_selection: Gtk.TreeSelection, wifi_card: str) -> None:
        """
        Handle WiFi network selection from the list.

        Args:
            tree_selection: TreeSelection containing the selected SSID
            wifi_card: Name of the wireless network interface
        """
        model, treeiter = tree_selection.get_selected()
        if treeiter is not None:
            ssid = model[treeiter][1]
            network = cls.networks[ssid]
            # Drop whatever an abandoned attempt left unsaved in the daemon.
            wpa_reconfigure(wifi_card)
            if ssid_is_saved(ssid, wifi_card):
                cls.connect_in_background(network, wifi_card)
            elif network['security'] == 'OPEN':
                if save_open_network(ssid, wifi_card) is None:
                    cls.wifi_connection_label.set_label(
                        get_text("Could not connect to {ssid}").format(ssid=ssid)
                    )
                    cls.wifi_connection_image.set_from_stock(Gtk.STOCK_NO, 5)
                else:
                    cls.connect_in_background(network, wifi_card)
            else:
                cls.authentication(network, wifi_card, False)

    @classmethod
    def add_to_wpa_supplicant(cls, _widget: Gtk.Widget, network: dict, card: str) -> None:
        """
        Add WiFi credentials to wpa_supplicant and attempt connection.

        Args:
            _widget: Widget that triggered this callback
            network: Access point record from scan_networks()
            card: Name of the wireless network interface
        """
        pwd = cls.password.get_text()
        ssid = network['ssid']
        cls.window.hide()
        wpa_reconfigure(card)
        if ssid_is_saved(ssid, card):
            stored = update_psk_network(ssid, pwd, card)
        else:
            stored = save_psk_network(ssid, network['security'], pwd, card) is not None
        if stored:
            cls.connect_in_background(network, card)
        else:
            cls.authentication(network, card, True)

    @classmethod
    def connect_in_background(cls, network: dict, card: str) -> None:
        """
        Run the connection attempt off the GTK thread.

        Args:
            network: Access point record from scan_networks()
            card: Name of the wireless network interface
        """
        threading.Thread(
            target=cls.try_to_connect_to_ssid,
            args=(network, card),
            daemon=True
        ).start()

    @classmethod
    def try_to_connect_to_ssid(cls, network: dict, card: str) -> None:
        """
        Attempt to connect to a WiFi network.

        Args:
            network: Access point record from scan_networks()
            card: Name of the wireless network interface
        """
        ssid = network['ssid']
        connected = connect_to_ssid(ssid, card) and wait_for_connection(card, ssid)
        # select_network disabled every other saved network. Re-enable them
        # before saving, or the file keeps them disabled for good.
        enable_all_networks(card)
        if connected:
            saved = wpa_save_config(card)
            GLib.idle_add(cls.connection_finished, network_dictionary(), ssid, saved)
        else:
            wpa_reconfigure(card)
            GLib.idle_add(cls.restart_authentication, network, card)

    @classmethod
    def connection_finished(cls, network_info: dict, ssid: str, saved: bool) -> None:
        """
        Show the new connection state once the card is connected.

        Args:
            network_info: Dictionary returned by network_dictionary()
            ssid: SSID of the network
            saved: False when wpa_supplicant.conf could not be written
        """
        cls.network_info = network_info
        print(cls.network_info)
        cls.update_network_detection()
        if not saved:
            cls.wifi_connection_label.set_label(
                get_text("Connected to {ssid}, but it could not be saved").format(ssid=ssid)
            )

    @classmethod
    def restart_authentication(cls, network: dict, card: str) -> None:
        """
        Restart authentication after failed connection attempt.

        Args:
            network: Access point record from scan_networks()
            card: Name of the wireless network interface
        """
        if network['security'] != 'OPEN':
            cls.authentication(network, card, True)

    @classmethod
    def on_check(cls, widget: Gtk.CheckButton) -> None:
        """
        Toggle password visibility in the authentication dialog.

        Args:
            widget: CheckButton widget that controls password visibility
        """
        if widget.get_active():
            cls.password.set_visibility(True)
        else:
            cls.password.set_visibility(False)

    @classmethod
    def authentication(cls, network: dict, card: str, failed: bool) -> str:
        """
        Display WiFi authentication dialog.

        Args:
            network: Access point record from scan_networks()
            card: Name of the wireless network interface
            failed: Whether previous authentication attempt failed

        Returns:
            str: Status message
        """
        cls.window = Gtk.Window()
        cls.window.set_title(get_text("WiFi Network Authentication Required"))
        cls.window.set_border_width(0)
        cls.window.set_size_request(500, 200)
        box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        cls.window.add(box1)
        box1.show()
        box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)
        box2.set_border_width(10)
        box1.pack_start(box2, True, True, 0)
        box2.show()
        # Creating MBR or GPT drive
        if failed:
            title = get_text("Could not connect to {ssid}").format(ssid=network['ssid'])
        else:
            title = get_text("Authentication required by") + " " + network['ssid'] + " " + get_text("Wi-Fi Network")
        label = Gtk.Label(label=f"<b><span size='large'>{title}</span></b>")
        label.set_use_markup(True)
        pwd_label = Gtk.Label(label=get_text("Password:"))
        cls.password = Gtk.Entry()
        cls.password.set_visibility(False)
        check = Gtk.CheckButton(label=get_text("Show password"))
        check.connect("toggled", cls.on_check)
        table = Gtk.Table(1, 2, True)
        table.attach(label, 0, 5, 0, 1)
        table.attach(pwd_label, 1, 2, 2, 3)
        table.attach(cls.password, 2, 4, 2, 3)
        table.attach(check, 2, 4, 3, 4)
        box2.pack_start(table, False, False, 0)
        box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=10)
        box2.set_border_width(5)
        box1.pack_start(box2, False, True, 0)
        box2.show()
        # Add create_scheme button
        cancel = Gtk.Button(stock=Gtk.STOCK_CANCEL)
        cancel.connect("clicked", cls.close)
        connect = Gtk.Button(stock=Gtk.STOCK_CONNECT)
        connect.connect("clicked", cls.add_to_wpa_supplicant, network, card)
        table = Gtk.Table(1, 2, True)
        table.set_col_spacings(10)
        table.attach(connect, 4, 5, 0, 1)
        table.attach(cancel, 3, 4, 0, 1)
        box2.pack_end(table, True, True, 5)
        cls.window.show_all()
        return 'Done'

    @classmethod
    def close(cls, _widget: Gtk.Widget) -> None:
        """
        Close the authentication dialog.

        Args:
            _widget: Widget that triggered this callback
        """
        cls.window.hide()