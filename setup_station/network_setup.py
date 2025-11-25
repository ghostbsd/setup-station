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
    networkdictionary,
    connectToSsid,
    delete_ssid_wpa_supplicant_config,
    nic_status
)
from setup_station.data import css_path

cssProvider = Gtk.CssProvider()
cssProvider.load_from_path(css_path)
screen = Gdk.Screen.get_default()
styleContext = Gtk.StyleContext()
styleContext.add_provider_for_screen(
    screen,
    cssProvider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


class NetworkSetup:
    """
    Utility class for network setup screen following the utility class pattern.

    Provides interface for detecting and configuring wired and wireless network connections.
    """
    # Class variables for UI state
    vbox1: Gtk.Box | None = None
    network_info: dict | None = None
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

                    wire_text = 'Network card connected to the internet'
                    cls.wire_connection_image.set_from_stock(Gtk.STOCK_YES, 5)
                    print('Connected True')
                    break
            else:
                wire_text = 'Network card not connected to the internet'
                cls.wire_connection_image.set_from_stock(Gtk.STOCK_NO, 5)
        else:
            wire_text = 'No network card detected'
            cls.wire_connection_image.set_from_stock(Gtk.STOCK_NO, 5)

        cls.wire_connection_label.set_label(wire_text)

        if wlan_list:
            for wlan_card in wlan_list:
                if cards[wlan_card]['state']['connection'] == 'Connected':
                    wifi_text = 'WiFi card detected and connected to an ' \
                        'access point'
                    cls.wifi_connection_image.set_from_stock(Gtk.STOCK_YES, 5)
                    break
            else:
                wifi_text = 'WiFi card detected but not connected to an ' \
                    'access point'
                cls.wifi_connection_image.set_from_stock(Gtk.STOCK_NO, 5)
        else:
            wifi_text = "WiFi card not detected or not supported"
            cls.wifi_connection_image.set_from_stock(Gtk.STOCK_NO, 5)

        cls.wifi_connection_label.set_label(wifi_text)

    @classmethod
    def initialize(cls) -> None:
        """
        Initialize the network setup UI.

        Detects network interfaces and creates the interface for wired/wireless setup.
        """
        cls.network_info = networkdictionary()
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
                    wire_text = 'Network card connected to the internet'
                    cls.wire_connection_image.set_from_stock(Gtk.STOCK_YES, 5)
                    print('Connected True')
                    break
            else:
                wire_text = 'Network card not connected to the internet'
                cls.wire_connection_image.set_from_stock(Gtk.STOCK_NO, 5)
        else:
            wire_text = 'No network card detected'
            cls.wire_connection_image.set_from_stock(Gtk.STOCK_NO, 5)

        cls.wire_connection_label.set_label(wire_text)
        wlan_card = ""
        if wlan_list:
            for wlan_card in wlan_list:
                if cards[wlan_card]['state']['connection'] == 'Connected':
                    wifi_text = 'WiFi card detected and connected to an ' \
                        'access point'
                    cls.wifi_connection_image.set_from_stock(Gtk.STOCK_YES, 5)
                    break
            else:
                wifi_text = 'WiFi card detected but not connected to an ' \
                    'access point'
                cls.wifi_connection_image.set_from_stock(Gtk.STOCK_NO, 5)
        else:
            wifi_text = 'WiFi card not detected or not supported'
            cls.wifi_connection_image.set_from_stock(Gtk.STOCK_NO, 5)

        cls.wifi_connection_label.set_label(wifi_text)

        cls.connection_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=True, spacing=20)
        if wlan_card:
            # add a default card variable
            sw = Gtk.ScrolledWindow()
            sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
            sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            cls.store = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str)
            for ssid in cls.network_info['cards'][wlan_card]['info']:
                ssid_info = cls.network_info['cards'][wlan_card]['info'][ssid]
                bar = ssid_info[4]
                stat = NetworkSetup.wifi_stat(bar)
                pixbuf = Gtk.IconTheme.get_default().load_icon(stat, 32, 0)
                cls.store.append([pixbuf, ssid, f'{ssid_info}'])
            treeview = Gtk.TreeView()
            treeview.set_model(cls.store)
            treeview.set_rules_hint(True)
            pixbuf_cell = Gtk.CellRendererPixbuf()
            pixbuf_column = Gtk.TreeViewColumn('Stat', pixbuf_cell)
            pixbuf_column.add_attribute(pixbuf_cell, "pixbuf", 0)
            pixbuf_column.set_resizable(True)
            treeview.append_column(pixbuf_column)
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn('SSID', cell, text=1)
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
            ssid_info = cls.network_info['cards'][wifi_card]['info'][ssid]
            caps = ssid_info[6]
            print(ssid)  # added the code to authenticate.
            print(ssid_info)
            if caps == 'E' or caps == 'ES':
                if f'"{ssid}"' in open("/etc/wpa_supplicant.conf").read():
                    cls.try_to_connect_to_ssid(ssid, ssid_info, wifi_card)
                else:
                    NetworkSetup.open_wpa_supplicant(ssid)
                    cls.try_to_connect_to_ssid(ssid, ssid_info, wifi_card)
            else:
                if f'"{ssid}"' in open('/etc/wpa_supplicant.conf').read():
                    cls.try_to_connect_to_ssid(ssid, ssid_info, wifi_card)
                else:
                    cls.authentication(ssid_info, wifi_card, False)

    @classmethod
    def add_to_wpa_supplicant(cls, _widget: Gtk.Widget, ssid_info: tuple, card: str) -> None:
        """
        Add WiFi credentials to wpa_supplicant config and attempt connection.

        Args:
            _widget: Widget that triggered this callback
            ssid_info: Tuple containing SSID information
            card: Name of the wireless network interface
        """
        pwd = cls.password.get_text()
        NetworkSetup.setup_wpa_supplicant(ssid_info[0], ssid_info, pwd)
        thr = threading.Thread(
            target=cls.try_to_connect_to_ssid,
            args=(ssid_info[0], ssid_info, card),
            daemon=True
        )
        thr.start()
        cls.window.hide()

    @classmethod
    def try_to_connect_to_ssid(cls, ssid: str, ssid_info: tuple, card: str) -> None:
        """
        Attempt to connect to a WiFi network.

        Args:
            ssid: SSID of the network
            ssid_info: Tuple containing SSID information
            card: Name of the wireless network interface
        """
        if connectToSsid(ssid, card) is False:
            delete_ssid_wpa_supplicant_config(ssid)
            GLib.idle_add(cls.restart_authentication, ssid_info, card)
        else:
            for _ in list(range(30)):
                if nic_status(card) == 'associated':
                    cls.network_info = networkdictionary()
                    print(cls.network_info)
                    cls.update_network_detection()
                    break
                sleep(1)
            else:
                delete_ssid_wpa_supplicant_config(ssid)
                GLib.idle_add(cls.restart_authentication, ssid_info, card)
        return

    @classmethod
    def restart_authentication(cls, ssid_info: tuple, card: str) -> None:
        """
        Restart authentication after failed connection attempt.

        Args:
            ssid_info: Tuple containing SSID information
            card: Name of the wireless network interface
        """
        cls.authentication(ssid_info, card, True)

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
    def authentication(cls, ssid_info: tuple, card: str, failed: bool) -> str:
        """
        Display WiFi authentication dialog.

        Args:
            ssid_info: Tuple containing SSID information
            card: Name of the wireless network interface
            failed: Whether previous authentication attempt failed

        Returns:
            str: Status message
        """
        cls.window = Gtk.Window()
        cls.window.set_title("wi-Fi Network Authentication Required")
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
            title = f"{ssid_info[0]} Wi-Fi Network Authentication failed"
        else:
            title = f"Authentication required by {ssid_info[0]} Wi-Fi Network"
        label = Gtk.Label(label=f"<b><span size='large'>{title}</span></b>")
        label.set_use_markup(True)
        pwd_label = Gtk.Label(label="Password:")
        cls.password = Gtk.Entry()
        cls.password.set_visibility(False)
        check = Gtk.CheckButton(label="Show password")
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
        connect.connect("clicked", cls.add_to_wpa_supplicant, ssid_info, card)
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

    @staticmethod
    def setup_wpa_supplicant(ssid: str, ssid_info: tuple, pwd: str) -> None:
        """
        Write WiFi credentials to wpa_supplicant configuration.

        Args:
            ssid: SSID of the network
            ssid_info: Tuple containing SSID security information
            pwd: Password for the network
        """
        if 'RSN' in ssid_info[-1]:
            ws = '\nnetwork={'
            ws += f'\n ssid="{ssid}"'
            ws += '\n key_mgmt=WPA-PSK'
            ws += '\n proto=RSN'
            ws += f'\n psk="{pwd}"\n'
            ws += '}\n'
        elif 'WPA' in ssid_info[-1]:
            ws = '\nnetwork={'
            ws += f'\n ssid="{ssid}"'
            ws += '\n key_mgmt=WPA-PSK'
            ws += '\n proto=WPA'
            ws += f'\n psk="{pwd}"\n'
            ws += '}\n'
        else:
            ws = '\nnetwork={'
            ws += f'\n ssid="{ssid}"'
            ws += '\n key_mgmt=NONE'
            ws += '\n wep_tx_keyidx=0'
            ws += f'\n wep_key0={pwd}\n'
            ws += '}\n'
        wsf = open("/etc/wpa_supplicant.conf", 'a')
        wsf.writelines(ws)
        wsf.close()

    @staticmethod
    def open_wpa_supplicant(ssid: str) -> None:
        """
        Add open (no password) WiFi network to wpa_supplicant configuration.

        Args:
            ssid: SSID of the network
        """
        ws = '\nnetwork={'
        ws += f'\n ssid={ssid}'
        ws += '\n key_mgmt=NONE\n}\n'
        with open("/etc/wpa_supplicant.conf", 'a') as wsf:
            wsf.writelines(ws)