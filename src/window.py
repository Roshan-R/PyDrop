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
import os, shutil

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk, Gdk, Gio, Adw, GObject, GLib
from gi.repository.GdkPixbuf import Pixbuf, PixbufLoader

from .utils import tools
from .parsedata import ParseData, BASE_DIR


@Gtk.Template(resource_path="/com/github/Roshan_R/PyDrop/ui/window.ui")
class PydropWindow(Adw.ApplicationWindow):
    __gtype_name__ = "PydropWindow"
    Adw.init()

    preview_image = Gtk.Template.Child()
    droparea = Gtk.Template.Child()
    button = Gtk.Template.Child()
    drag_source = Gtk.Template.Child()
    stack = Gtk.Template.Child()
    spinner_box = Gtk.Template.Child()
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
        self.initial = True
        self.parser = ParseData(self.on_download)

        if os.path.exists(BASE_DIR):
            shutil.rmtree(BASE_DIR)
        os.makedirs(BASE_DIR, exist_ok=True)

    def setup_signals(self):
        target = Gtk.DropTarget(actions=Gdk.DragAction.COPY)
        target.set_gtypes([Gdk.Texture, Gdk.FileList, GObject.TYPE_STRING])
        target.connect("drop", self.on_drop)
        target.connect("accept", self.on_accept)
        self.droparea.add_controller(target)

        self.drag_source = Gtk.DragSource()
        self.drag_source.connect("prepare", self.on_drag_prepare)
        self.drag_source.connect("drag-begin", self.on_drag_begin)

        event_controller_key = Gtk.EventControllerKey()
        event_controller_key.connect("key-released", self.on_key_release)
        self.add_controller(event_controller_key)

    def on_download(self):
        match self.stack.get_visible_child().get_buildable_id():
            case "initial_stack" | "eventbox":
                self.stack.set_visible_child(self.spinner_box)
            case "spinner_box":
                self.stack.set_visible_child(self.eventbox)

    def on_drop(self, target, value, x, y):
        # Only add controller to Droparea once something is DnD'd to the app.
        if self.initial:
            self.droparea.add_controller(self.drag_source)
            self.initial = False
            self.stack.set_visible_child(self.eventbox)
            self.button.set_visible(True)

        def on_parse_complete(count, mime_type):
            self.count = count
            self.button.set_label(f"{self.count} Files")
            tools.set_image(self.link_stack, self.preview_image, mime_type)

        self.parser.parse(value, self.link_stack, self.count, on_parse_complete)

    def on_accept(self, target, drop):
        drag = drop.get_drag()
        # Do no accept DnD operations from the app itself
        if drag and drag.get_surface() == self.get_surface():
            return False
        return True

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

    def on_drag_begin(self, drag_source, widget):
        if self.preview_image.get_gicon():
            paintable = tools.get_paintable_from_gicon(self.preview_image.get_gicon())
        else:
            paintable = self.preview_image.get_paintable()
        drag_source.set_icon(paintable, 0, 0)

    # TODO: document this behaviour somewhere
    def on_key_release(self, event_controller_key, keycode, *args):
        if keycode == Gdk.KEY_Escape:
            self.close()
