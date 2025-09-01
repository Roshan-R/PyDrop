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

from .dropped_item import DroppedItem
from .utils import tools
from .parsedata import ParseData, BASE_DIR
import gi
import os
import shutil

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk, Gdk, Adw, GObject, GLib, Gio  # noqa


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
    initial_stack = Gtk.Template.Child()
    grid_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_variables()
        self.setup_signals()
        self.setup_gridview()

    def setup_variables(self):
        self.count = 0
        self.dropped_items: list[DroppedItem] = []
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

    def setup_gridview(self):
        self.list_store = Gio.ListStore()
        # TODO: might have to change this
        ss = Gtk.SingleSelection()
        ss.set_model(self.list_store)
        self.grid_view.set_model(ss)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._on_factory_setup)
        factory.connect("bind", self._on_factory_bind)

        self.grid_view.set_factory(factory)

    def _on_factory_setup(self, fact, item):
        """
        Gtk.Overlay
        ├── Gtk.Box (Vertical)
        │   ├── Gtk.Image
        │   └── Gtk.Label
        └── Gtk.Button (Overlay: top-right, close icon)
        """
        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        image = Gtk.Image()
        image.set_pixel_size(150)
        box.append(image)
        label = Gtk.Label()
        box.append(label)

        button = Gtk.Button.new_from_icon_name("window-close-symbolic")
        button.set_halign(Gtk.Align.END)
        button.set_valign(Gtk.Align.START)
        button.add_css_class("destructive-action")
        button.connect("clicked", self._remove_item_on_button_click)

        overlay = Gtk.Overlay()
        overlay.set_child(box)
        overlay.add_overlay(button)
        item.set_child(overlay)

    def _on_factory_bind(self, fact, item):
        overlay = item.get_child()
        box = overlay.get_child()
        image = box.get_first_child()
        label = box.get_last_child()

        dropped_item = item.get_item()
        image.set_from_paintable(dropped_item.paintable)
        label.set_label(dropped_item.file_name)

        # Set the model item on the button for later access
        button = overlay.get_last_child()
        button.data = dropped_item

    def _remove_item_on_button_click(self, button):
        got_it, position = self.list_store.find(button.data)
        if not got_it:
            raise Exception("Cannot find the element for deletion")
        self.list_store.remove(position)
        self.dropped_items.remove(button.data)
        self._refresh_ui_on_dropped_items_change()

    def _refresh_ui_on_dropped_items_change(self):
        # TODO: change this logic to be better
        self.count = len(self.dropped_items)
        if self.count == 0:
            self.stack.set_visible_child(self.initial_stack)
        else:
            self.stack.set_visible_child(self.eventbox)

        self.button.set_label(f"{self.count} Files")
        tools.set_image(self.dropped_items, self.preview_image)


    def on_download(self):
        match self.stack.get_visible_child().get_buildable_id():
            case "initial_stack" | "eventbox":
                self.stack.set_visible_child(self.spinner_box)
            case "spinner_box":
                self.stack.set_visible_child(self.eventbox)

    def on_drop(self, target, value, x, y):
        self.parser.parse(value, self.dropped_items, self.count, self.on_parse_complete)

    def on_parse_complete(self, count, mime_type=None):
        # Only add controller to Droparea once something is DnD'd to the app.
        if self.initial:
            self.initial = False
            self.eventbox.add_controller(self.drag_source)
            self.stack.set_visible_child(self.eventbox)

        self.list_store.remove_all()
        for item in self.dropped_items:
            self.list_store.append(item)

        self._refresh_ui_on_dropped_items_change()

    def on_accept(self, target, drop):
        drag = drop.get_drag()
        # Do no accept DnD operations from the app itself
        if drag and drag.get_surface() == self.get_surface():
            return False
        return True

    def on_drag_prepare(self, source, x, y):
        # TODO: just working with files right now
        # Took from: https://github.com/mijorus/collector/blob/master/src/window.py
        uri_list = "\n".join([f"file://{f.file_path}" for f in self.dropped_items])
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
        drag_source.set_icon(paintable, 75, 75)

    # TODO: document this behaviour somewhere
    def on_key_release(self, event_controller_key, keycode, *args):
        if keycode == Gdk.KEY_Escape:
            self.close()
