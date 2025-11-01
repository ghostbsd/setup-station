#!/usr/bin/env python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from setup_station.common import password_strength

cssProvider = Gtk.CssProvider()
cssProvider.load_from_path('/usr/local/lib/setup-station/ghostbsd-style.css')
screen = Gdk.Screen.get_default()
styleContext = Gtk.StyleContext()
styleContext.add_provider_for_screen(
    screen,
    cssProvider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


class AddUsers:

    def save_selection(self):
        uname = self.user.get_text()
        name = self.name.get_text()
        up = self.password.get_text()
        shell = self.sh
        hf = '/home/%s' % self.user.get_text()
        hst = self.host.get_text()
        ul = [uname, name, up, shell, hf]

    def on_shell(self, widget):
        SHELL = widget.get_active_text()
        if SHELL == 'sh':
            self.sh = '/bin/sh'
        elif SHELL == 'csh':
            self.sh = '/bin/csh'
        elif SHELL == 'tcsh':
            self.sh = '/bin/tcsh'
        elif SHELL == 'fish':
            self.sh = '/usr/local/bin/fish'
        elif SHELL == 'bash':
            self.sh = '/usr/local/bin/bash'
        elif SHELL == 'rbash':
            self.sh = '/usr/local/bin/rbash'
        elif SHELL == 'zsh':
            self.sh = '/usr/local/bin/zsh'
        elif SHELL == 'ksh':
            self.sh = '/usr/local/bin/ksh93'

    def user_and_host(self, _widget):
        username = self.name.get_text().split()
        self.host.set_text("%s-ghostbsd-pc" % username[0].lower())
        self.user.set_text(username[0].lower())

    def __init__(self, button3):
        self.vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        self.vbox1.show()
        title = Gtk.Label(label="User Setup", name="Header")
        title.set_property("height-request", 50)
        self.vbox1.pack_start(title, False, False, 0)
        box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        box2.set_border_width(10)
        self.vbox1.pack_start(box2, False, False, 0)
        box2.show()
        box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)
        # box2.set_border_width(10)
        self.vbox1.pack_start(box2, False, False, 0)
        box2.show()
        label = Gtk.Label(label='<b>User Account</b>')
        label.set_use_markup(True)
        label.set_alignment(.2, .2)
        Username = Gtk.Label(label="User name")
        self.user = Gtk.Entry()
        self.label2 = Gtk.Label(label="Real name")
        self.name = Gtk.Entry()
        self.name.connect("changed", self.user_and_host)
        self.labelpass = Gtk.Label(label="Password")
        self.password = Gtk.Entry()
        self.password.set_visibility(False)
        self.password.connect("changed", self.password_verification, button3)
        self.label4 = Gtk.Label(label="Verify Password")
        self.repassword = Gtk.Entry()
        self.repassword.set_visibility(False)
        self.repassword.connect("changed", self.password_verification, button3)
        self.label5 = Gtk.Label(label="Shell")
        shell = Gtk.ComboBoxText()
        self.sh = '/usr/local/bin/fish'
        shell.append_text('sh')
        shell.append_text('csh')
        shell.append_text('tcsh')
        shell.append_text('fish')
        shell.append_text('bash')
        shell.append_text('rbash')
        shell.append_text('ksh')
        shell.append_text('zsh')
        shell.set_active(3)
        shell.connect("changed", self.on_shell)
        label = Gtk.Label(label='<b>Set Hostname</b>')
        label.set_use_markup(True)
        label.set_alignment(0, .5)
        table = Gtk.Table(1, 3, True)
        table.set_row_spacings(10)
        pcname = Gtk.Label(label="Hostname")
        self.host = Gtk.Entry()
        # table.attach(label, 0, 2, 0, 1)
        table.attach(self.label2, 0, 1, 1, 2)
        table.attach(self.name, 1, 2, 1, 2)
        table.attach(pcname, 0, 1, 2, 3)
        table.attach(self.host, 1, 2, 2, 3)
        table.attach(Username, 0, 1, 3, 4)
        table.attach(self.user, 1, 2, 3, 4)
        table.attach(self.labelpass, 0, 1, 4, 5)
        table.attach(self.password, 1, 2, 4, 5)
        self.label3 = Gtk.Label()
        table.attach(self.label3, 2, 3, 4, 5)
        table.attach(self.label4, 0, 1, 5, 6)
        table.attach(self.repassword, 1, 2, 5, 6)
        # set image for password matching
        self.img = Gtk.Image()
        table.attach(self.img, 2, 3, 5, 6)
        table.attach(self.label5, 0, 1, 6, 7)
        table.attach(shell, 1, 2, 6, 7)
        box2.pack_start(table, False, False, 0)
        self.box3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)
        self.box3.set_border_width(10)
        self.vbox1.pack_start(self.box3, True, True, 0)
        self.box3.show()
        # self.label3 = Gtk.Label()
        # self.box3.pack_start(self.label3, False, False, 0)

    def get_model(self):
        return self.vbox1

    def password_verification(self, _widget, button3):
        password = self.password.get_text()
        password_strength(password, self.label3)
        repassword = self.repassword.get_text()
        if password == repassword and password != "" and " " not in password:
            self.img.set_from_stock(Gtk.STOCK_YES, 5)
            button3.set_sensitive(True)
        else:
            self.img.set_from_stock(Gtk.STOCK_NO, 5)
            button3.set_sensitive(False)
