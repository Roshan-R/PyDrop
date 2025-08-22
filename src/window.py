# window.py
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

import gi
import os

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk, Gdk, Gio, Adw, GObject, GLib
from gi.repository.GdkPixbuf import Pixbuf, PixbufLoader

from .utils import tools
from .parsedata import ParseData

(TARGET_OCTECT_STREAM, TARGET_PNG, TARGET_URI_LIST, TARGET_PLAIN) = range(4)


@Gtk.Template(resource_path="/com/github/Roshan_R/PyDrop/ui/window.ui")
class PydropWindow(Adw.ApplicationWindow):
    __gtype_name__ = "PydropWindow"

    Adw.init()

    icon = Gtk.Template.Child()
    droparea = Gtk.Template.Child()
    button = Gtk.Template.Child()
    drag_source = Gtk.Template.Child()
    stack = Gtk.Template.Child()
    spinner = Gtk.Template.Child()
    eventbox = Gtk.Template.Child()
    # TODO : make iconview
    # iconview = Gtk.Template.Child()
    initial_stack = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_variables()
        self.setup_signals()

    def setup_variables(self):
        self.button.hide()
        self.count = 0
        self.link_stack = []
        self.initial = 1

        self.parser = ParseData()

        import subprocess

        # TODO : better temporary directory?
        if not os.path.exists("/tmp/pydrop"):
            os.mkdir("/tmp/pydrop")
            out = subprocess.check_output(["ls", "/tmp/pydrop"])
            print("Output is: ", out)
        else:
            out = subprocess.check_output(["ls", "/tmp/pydrop"])
            print("Already existing Output is: ", out)

    def setup_signals(self):
        target = Gtk.DropTarget(actions=Gdk.DragAction.COPY)
        target.set_gtypes([Gdk.Texture, Gdk.FileList, GObject.TYPE_STRING])
        target.connect("drop", self.on_drop)
        self.droparea.add_controller(target)

        source = Gtk.DragSource()
        source.connect("prepare", self.on_drag_prepare)
        source.connect("drag-begin", self.on_drag_begin)
        self.droparea.add_controller(source)

        # self.connect("key-press-event", self.key_press_event)

    def on_drop(self, target, value, x, y):
        count, mime_type = self.parser.parse(value, self.link_stack, self.count)
        print(mime_type)
        self.count = count
        tools.set_image(self.link_stack, self.icon, mime_type)
        self.stack.set_visible_child(self.eventbox)
        self.button.set_label(str(self.count) + " Files")
        self.button.set_visible(True)

    def on_drag_prepare(self, source, x, y):
        # TODO: just working with files right now
        # Took from: https://github.com/mijorus/collector/blob/master/src/window.py
        uri_list = "\n".join([f"file://{f}" for f in self.link_stack])
        return Gdk.ContentProvider.new_union(
            [
                Gdk.ContentProvider.new_for_bytes(
                    "text/uri-list", GLib.Bytes.new(uri_list.encode())
                )
            ]
        )

    def on_drag_begin(self, source, widget):
        # Change drag icon here?
        print(source, widget)

        def change_drag_icon(self, widget, data):
            self.dropped = 0
            if self.icon.get_pixbuf():
                Gtk.drag_set_icon_pixbuf(data, self.icon.get_pixbuf(), 0, 0)
            else:
                Gtk.drag_set_icon_gicon(data, self.icon.get_gicon()[0], 0, 0)
            if self.initial != 1:
                pass
            # self.icon.clear()

    # TODO: replace to GtkEventControllerKey
    def key_press_event(self, _a, event_key):
        if event_key.keyval == Gdk.KEY_Escape:
            self.close()
