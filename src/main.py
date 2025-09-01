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

from .window import PydropWindow
import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Gio, Adw, Gdk  # noqa


def apply_custom_css():
    css = b"""
    gridview {
        background-color: @popover_bg_color;
    }
"""
    provider = Gtk.CssProvider()
    provider.load_from_data(css)

    display = Gdk.Display.get_default()
    Gtk.StyleContext.add_provider_for_display(
        display, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
    )


class Application(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.Roshan_R.PyDrop",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
            resource_base_path="/com/github/Roshan_R/PyDrop/",
        )
        apply_custom_css()
        action = Gio.SimpleAction(name="about")
        action.connect("activate", self.show_about_dialog)
        self.add_action(action)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = PydropWindow(application=self)
        win.present()

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
