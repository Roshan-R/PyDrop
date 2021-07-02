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
import validators
import io


from urllib.parse import unquote
import magic
import requests
from PIL import Image
import os


import threading

#(TARGET_ENTRY_URI, TARGET_ENTRY_TEXT, TARGET_ENTRY_MOZ_URL) = range(3)
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
    iconview = Gtk.Template.Child()
    initial_stack = Gtk.Template.Child()

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):

        print(info)
        
        # TODO : handle this section better

        # Application/Octect stream
        if info == TARGET_OCTECT_STREAM:
            image = Image.open(io.BytesIO(data.get_data()))
            format = image.format.lower()
            image.save(f"/tmp/pydrop/{self.count}.{format}")
            x = self.icon.get_pixel_size() + 50
            pixbuf = Pixbuf.new_from_file_at_scale(f"/tmp/pydrop/{self.count}.{format}", x, x, True)
            print("This in an image")
            self.link_stack.append(f"file:///tmp/pydrop/{self.count}.{format}")
            self.icon.set_from_pixbuf(pixbuf)
            self.count += 1
            a = "special"

        # plain

        # TODO : Make a file for plain text with first word as filename

        if info == TARGET_PLAIN:
            print("Got some good old plain text")
            print(data.get_text())

        if info == TARGET_URI_LIST:
            print(data.get_uris())
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

            if self.is_link(text):
                link = text
                x = self.google_re.findall(link)
                if x:
                    link = unquote(x[0])
                    print("this is a google image : ", link)
                    print("Google image link : ", link)
                    self.download_image(link)
                    a = "special"

                elif self.link_is_image(link):                                            
                    self.download_image(link)
                    # trying out multithreading so ui does not get blocked
                    # while loading image

                    #download_thread = threading.Thread(target=self.download_image, args=(link,))
                    #download_thread.start()
                    #download_thread.join()
                    a = "special"
                else:
                    self.link_stack.append(link)
                    a = "text/html"
            
            else:
                print(data.get_text())
                a = "text/plain"
            self.count += 1


        print(a)

        if "special" not in a:
            if "image" in a:
                x = self.icon.get_pixel_size() + 50

                pixbuf = Pixbuf.new_from_file_at_scale(uri[6:].replace('%20', ' '), x, x, True)
                print("This in an image")
                self.icon.set_from_pixbuf(pixbuf)

            else:
                gicon = Gio.content_type_get_icon(a)
                self.icon.set_from_gicon(gicon, 512)
        self.stack.set_visible_child(self.eventbox)
        self.button.set_label(str(self.count) + " Files")

        if self.initial == 1:
            source_targets = [
                Gtk.TargetEntry.new("text/uri-list", Gtk.TargetFlags(4), TARGET_URI_LIST),
                Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags(4), TARGET_PLAIN),
            ]

            self.eventbox.drag_source_set(
                Gdk.ModifierType.BUTTON1_MASK, source_targets, Gdk.DragAction.COPY
            )
            self.eventbox.connect("drag-begin", self.hello)
            self.eventbox.connect("drag-data-get", self.on_drag_data_get)
            self.eventbox.connect("drag-end", self.end)
            self.initial = 0
            self.button.show()


    def is_link(self, text):
        if validators.url(text):
            return True
        else:
            return False

    def link_is_image(self, link):

        """"
            returns True is link is an image
            else False

            https://stackoverflow.com/questions/10543940/check-if-a-url-to-an-image-is-up-and-exists-in-python
        """

        self.image_formats = ("image/png", "image/jpeg", "image/jpg")
        r = requests.head(link)
        if r.headers["content-type"] in self.image_formats:
            return True
        return False
        

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

    def hello(self, widget, data):
        print(widget, data)
        #Gtk.drag_set_icon_name(data, 'gtk-dnd', 0, 0)
        if self.icon.get_pixbuf():
            Gtk.drag_set_icon_pixbuf(data, self.icon.get_pixbuf(), 0, 0)
        else:
            print(self.icon.get_gicon())
            Gtk.drag_set_icon_gicon(data, self.icon.get_gicon()[0], 0, 0)


        if self.initial != 1:
            pass
            #self.icon.clear()
        print("Hello world")

    def hello_source(self, widget, drag_context, x, y, data):
        print("soure activated")
        self.stack.set_visible_child(self.spinner)

    def on_drag_data_get(self, widget, drag_context, data, info, time):
        # print(info)
        data.set_uris(self.link_stack)


    def end(self, data, info):
        print("Closing Window")
        #self.close()

    def change_cursor(self, widget, event ):
        if not self.initial:
            c = Gdk.Cursor(Gdk.CursorType.HAND1)
            print(self)
            widget.get_window().set_cursor(c)

    def revert_cursor(self, widget, event ):
        print("The cursor has leaved the area")

    def drop_source(self, widget, drag_context, x, y, time, data):
        print("DROPPED MMMEEE")
        self.stack.set_visible_child(self.eventbox)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.google_re = re.compile(
            "[http|https]:\/\/www.google.com\/imgres\?imgurl=(.*)\&imgrefurl"
        )
        print(self.iconview.get_model())
        self.button.hide()
        self.image_formats = ("image/png", "image/jpeg", "image/jpg")
        self.count = 0
        self.link_stack = []
        self.initial = 1
        self.stick()
        self.set_keep_above(True)

        # TODO : better temporary directory?
        if not os.path.exists('/tmp/pydrop'):
            os.mkdir("/tmp/pydrop")

        # drop destination stuff

        enforce_target = [
            Gtk.TargetEntry.new("application/octet-stream", Gtk.TargetFlags(4), TARGET_OCTECT_STREAM),
            Gtk.TargetEntry.new("text/uri-list", Gtk.TargetFlags(4), TARGET_URI_LIST),
            Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags(4), TARGET_PLAIN),
        ]

        self.droparea.drag_dest_set(
            Gtk.DestDefaults.ALL, enforce_target, Gdk.DragAction.COPY
        )
        self.droparea.connect("drag-data-received", self.on_drag_data_received)
        self.droparea.connect("drag-drop", self.hello_source)

        self.eventbox.connect("enter-notify-event", self.change_cursor)
        self.eventbox.connect("leave-notify-event", self.revert_cursor)

