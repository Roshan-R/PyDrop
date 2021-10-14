# main.py
#
# Copyright 2021 Roshan-R
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Gdk, GLib, Adw

from .window import PydropWindow

class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.github.Roshan_R.PyDrop',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        #css_provider = Gtk.CssProvider()
        #css_provider.load_from_resource('/com/github/Roshan_R/PyDrop/css/style.css')
        #Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.setup_actions()

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = PydropWindow(application=self)
        win.present()

    def setup_actions(self):
        action = Gio.SimpleAction(name="about")
        action.connect("activate", self.show_about_dialog)
        self.add_action(action)

    def show_about_dialog(self, action, param):
        about = Gtk.AboutDialog()
        about.set_transient_for(self.get_active_window())
        about.set_modal(True)
        # about.set_version(self.version)
        about.set_program_name("PyDrop")
        about.set_logo_icon_name("com.github.Roshan_R.PyDrop")
        about.set_authors(["Roshan R Chandar"])
        about.set_comments(_("An Opensource alternative to Dropover"))
        about.set_wrap_license(True)
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_copyright(_("Copyright 2021 Roshan R Chandar"))
        # Translators: Replace "translator-credits" with your names, one name per line
        about.set_translator_credits(_("translator-credits"))
        about.set_website_label(_("GitHub"))
        about.set_website("https://github.com/Roshan-R/PyDrop")
        about.present()

def main(version):
    app = Application()
    return app.run(sys.argv)
