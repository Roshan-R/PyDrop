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

gi.require_version('Handy', '1')
from gi.repository import Gtk, Gdk, Gio, Handy
from gi.repository.GdkPixbuf import Pixbuf, PixbufLoader

import re
import io

from urllib.parse import unquote
import magic
import requests
from PIL import Image
import os
from .utils import tools


import threading

(TARGET_OCTECT_STREAM, TARGET_URI_LIST, TARGET_PLAIN) = range(3)


@Gtk.Template(resource_path="/com/github/Roshan_R/PyDrop/window.ui")
class PydropWindow(Handy.Window):
    __gtype_name__ = "PydropWindow"

    Handy.init()
    icon = Gtk.Template.Child()
    headerbar = Gtk.Template.Child()
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
        self.google_re = re.compile(
                "[http|https]:\/\/www.google.com\/imgres\?imgurl=(.*)\&imgrefurl"
                )
        self.image_size = self.icon.get_pixel_size() + 50
        #print(self.iconview.get_model())
        self.button.hide()
        self.image_formats = ["image/png", "image/jpeg", "image/jpg"]
        self.count = 0
        self.link_stack = []
        self.initial = 1
        self.stick()
        self.set_keep_above(True)

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
        # self.droparea.connect("drag-drop", self.hello_source)

        # self.eventbox.connect("enter-notify-event", self.change_cursor)
        # self.eventbox.connect("leave-notify-event", self.revert_cursor)
        #self.connect("delete-event", self.hide_the_window)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):

        # TODO: better printing debug information

        # Application/Octect stream : Image from Chromuim browsers
        if info == TARGET_OCTECT_STREAM:
            print("Got an Image from browser")
            image = Image.open(io.BytesIO(data.get_data()))
            format = image.format.lower()
            image.save(f"/tmp/pydrop/{self.count}.{format}")
            x = self.icon.get_pixel_size() + 50
            pixbuf = Pixbuf.new_from_file_at_scale(f"/tmp/pydrop/{self.count}.{format}", x, x, True)
            self.link_stack.append(f"file:///tmp/pydrop/{self.count}.{format}")
            self.icon.set_from_pixbuf(pixbuf)
            self.count += 1
            a = "special"

        if info == TARGET_URI_LIST:
            # print(data.get_uris())
            for uri in data.get_uris():
                print(uri)
                self.link_stack.append(uri)
                self.count += 1
                mime = magic.Magic(mime=True)
            try:
                a = mime.from_file(uri[7:].replace('%20', ' '))
            except IsADirectoryError:
                a = "inode/directory"

        elif info == TARGET_PLAIN:

            text = data.get_text()
            print(text)

            if tools.is_link(text):
                link = text
                x = self.google_re.findall(link)
                if x:
                    link = unquote(x[0])
                    print("this is a google image : ", link)
                    print("Google image link : ", link)
                    self.download_image(link)
                    a = "special"

                elif tools.link_is_image(link):
                    self.download_image(link)
                    a = "special"
                else:
                    # TODO: handle link better, preferably make a file that contains the link?
                    # investigate on which filetype to use
                    self.link_stack.append(link)
                    a = "text/html"

            else:
                print(" Got text ")
                file_name = f'{text.split()[0]}.txt'
                file_path = f'/tmp/pydrop/{file_name}'
                with open(f'{file_path}', 'w+') as f:
                    f.write(text)
                self.link_stack.append(f'file://{file_path}')
                a = "text/plain"

            self.count += 1


        print(a)

        if "special" not in a:
            if a in self.image_formats:

                # TODO  : add preview support for more mime types
                #          - gifs
                #          - videos
                #          - pdfs

                pixbuf = Pixbuf.new_from_file_at_scale(
                        uri[6:].replace('%20', ' '),
                        self.image_size,
                        self.image_size,
                        True)
                self.icon.set_from_pixbuf(pixbuf)
            else:
                gicon = Gio.content_type_get_icon(a)
                self.icon.set_from_gicon(gicon, 512)
        self.stack.set_visible_child(self.eventbox)
        self.button.set_label(str(self.count) + " Files")

        if self.initial == 1:

            # Drag Dest

            source_targets = [
                    Gtk.TargetEntry.new("text/uri-list", Gtk.TargetFlags(4), TARGET_URI_LIST),
                    Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags(4), TARGET_PLAIN),
                    ]

            self.eventbox.drag_source_set(
                    Gdk.ModifierType.BUTTON1_MASK, source_targets, Gdk.DragAction.COPY
                    )
            self.eventbox.connect("drag-begin", self.change_drag_icon)
            self.eventbox.connect("drag-data-get", self.on_drag_data_get)
            self.eventbox.connect("drag-end", self.end)
            self.initial = 0
            self.button.show()

    def download_image(self, link):

        # TODO: make the download another thread

        print(link)
        print("Starting download...")
        r = requests.get(link)

        extension = r.headers["content-type"].split('/')[1]
        self.file_path = f"/tmp/pydrop/{self.count}.{extension}"

        with open(self.file_path, "wb") as f:
            f.write(r.content)
        x = self.icon.get_pixel_size() + 50
        pixbuf = Pixbuf.new_from_file_at_scale(self.file_path, x, x, True)
        self.icon.set_from_pixbuf(pixbuf)
        self.link_stack.append(f"file://{self.file_path}")
        return 1

    def change_drag_icon(self, widget, data):
        if self.icon.get_pixbuf():
            Gtk.drag_set_icon_pixbuf(data, self.icon.get_pixbuf(), 0, 0)
        else:
            # print(self.icon.get_gicon())
            Gtk.drag_set_icon_gicon(data, self.icon.get_gicon()[0], 0, 0)
        if self.initial != 1:
            pass
        #self.icon.clear()

    # def hello_source(self, widget, drag_context, x, y, data):
        # print("soure activated")
        # self.stack.set_visible_child(self.spinner)

    def on_drag_data_get(self, widget, drag_context, data, info, time):
        # print(info)
        data.set_uris(self.link_stack)


    def end(self, _a, drag_context):
        print("DragContext : " , drag_context.get_dest_window())
        print("DragProtocol : " , drag_context.get_protocol())
        print("Closing Window")
        self.close()

    # def change_cursor(self, widget, event ):
        # if not self.initial:
            # c = Gdk.Cursor(Gdk.CursorType.HAND1)
            # widget.get_window().set_cursor(c)

    # def revert_cursor(self, widget, event ):
        # print("The cursor has leaved the area")

    # def drop_source(self, widget, drag_context, x, y, time, data):
        # print("DROPPED MMMEEE")
        # self.stack.set_visible_child(self.eventbox)

    # def hide_the_window(self, a, b):
        # print("Hiding the window")
        # self.stick()
        # self.set_keep_above(True)
        # return self.hide_on_delete()

