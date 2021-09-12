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

gi.require_version('Handy', '1')
from gi.repository import Gtk, Gdk, Gio, Handy
from gi.repository.GdkPixbuf import Pixbuf, PixbufLoader

from .utils import tools
from .parsedata import ParseData

(TARGET_OCTECT_STREAM, TARGET_URI_LIST, TARGET_PLAIN) = range(3)


@Gtk.Template(resource_path="/com/github/Roshan_R/PyDrop/ui/window.ui")
class PydropWindow(Handy.Window):
    __gtype_name__ = "PydropWindow"

    Handy.init()
    icon = Gtk.Template.Child()
    droparea = Gtk.Template.Child()
    button = Gtk.Template.Child()
    drag_source = Gtk.Template.Child()
    stack = Gtk.Template.Child()
    spinner = Gtk.Template.Child()
    eventbox = Gtk.Template.Child()
    # TODO : make iconview
    #iconview = Gtk.Template.Child()
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
        self.stick()
        self.set_keep_above(True)
        self.parser = ParseData()

        # TODO : better temporary directory?
        if not os.path.exists('/tmp/pydrop'):
            os.mkdir("/tmp/pydrop")

    def setup_signals(self):

        # Drop Target
        enforce_target = [
                Gtk.TargetEntry.new("application/octet-stream", Gtk.TargetFlags(4), TARGET_OCTECT_STREAM),
                Gtk.TargetEntry.new("text/uri-list", Gtk.TargetFlags(4), TARGET_URI_LIST),
                Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags(4), TARGET_PLAIN),
                ]

        self.droparea.drag_dest_set(
                Gtk.DestDefaults.ALL, enforce_target, Gdk.DragAction.COPY
                )
        self.droparea.connect("drag-data-received", self.on_drag_data_received)

    def connect_drag_source(self):
        source_targets = [
                Gtk.TargetEntry.new("text/uri-list", Gtk.TargetFlags(4), TARGET_URI_LIST),
                Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags(4), TARGET_PLAIN),
                ]
        self.eventbox.drag_source_set(
                Gdk.ModifierType.BUTTON1_MASK, source_targets, Gdk.DragAction.COPY
                )
        self.eventbox.connect("drag-begin", self.change_drag_icon)
        self.eventbox.connect("drag-data-get", self.on_drag_data_get)
        self.initial = 0
        self.button.show()

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        count, a = self.parser.parse(data, info, self.link_stack, self.count)
        print(self.link_stack)
        self.count = count
        tools.set_image(self.link_stack, self.icon, a)
        self.stack.set_visible_child(self.eventbox)
        self.button.set_label(str(self.count) + " Files")

        if self.initial == 1:
            self.connect_drag_source()

    def on_drag_data_get(self, widget, drag_context, data, info, time):
        drag_context.connect("dnd-finished", self.finished)
        data.set_uris(self.link_stack)

    def finished(self, _a):
        self.close()

    def change_drag_icon(self, widget, data):
        self.dropped = 0
        if self.icon.get_pixbuf():
            Gtk.drag_set_icon_pixbuf(data, self.icon.get_pixbuf(), 0, 0)
        else:
            Gtk.drag_set_icon_gicon(data, self.icon.get_gicon()[0], 0, 0)
        if self.initial != 1:
            pass
        #self.icon.clear()
