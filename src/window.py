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

from gi.repository import Gtk, Gdk, Gio
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

(TARGET_ENTRY_URI, TARGET_ENTRY_TEXT, TARGET_ENTRY_MOZ_URL) = range(3)


@Gtk.Template(resource_path="/com/github/Roshan_R/PyDrop/window.ui")
class PydropWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "PydropWindow"

    icon = Gtk.Template.Child()
    headerbar = Gtk.Template.Child()
    droparea = Gtk.Template.Child()
    button = Gtk.Template.Child()
    drag_source = Gtk.Template.Child()
    stack = Gtk.Template.Child()
    spinner = Gtk.Template.Child()

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        print(info)

        
        # Application/Octect stream
        if info == 123:
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
        # text/html

        if info == 321:
            print(data.get_text())

        if info == TARGET_ENTRY_URI:
            print(data.get_uris())
            for uri in data.get_uris():
                print(uri)
                self.link_stack.append(uri)
                self.count += 1
                mime = magic.Magic(mime=True)
            try:
                a = mime.from_file(uri[6:])
            except IsADirectoryError:
                a = "inode/directory"
        elif info == TARGET_ENTRY_TEXT:

            
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


        elif info == TARGET_ENTRY_MOZ_URL:
            print("hello?")

        print(a)

        if "special" not in a:
            if "image" in a:
                x = self.icon.get_pixel_size() + 50
                pixbuf = Pixbuf.new_from_file_at_scale(uri[6:], x, x, True)
                print("This in an image")
                self.icon.set_from_pixbuf(pixbuf)
                # self.icon.set_from_file(uri[6:])
            else:
                #icon_name = Gio.content_type_get_generic_icon_name(a)
                #print(icon_name)
                gicon = Gio.content_type_get_icon(a)
                self.icon.set_from_gicon(gicon, 512)
        self.stack.set_visible_child(self.icon)
        self.button.set_label(str(self.count) + " Files")
        if self.initial == 1:
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
        print("Hello world")

    def hello_source(self, widget, drag_context, x, y, data):
        print("soure activated")
        print(widget, drag_context, x, y, data)
        self.stack.set_visible_child(self.spinner)

    def on_drag_data_get(self, widget, drag_context, data, info, time):
        # print(info)
        print(widget, drag_context, data.get_data_type(), info, time)
        print(self.link_stack)
        print(data.get_target())
        data.set_uris(self.link_stack)


    def end(self, data, info):
        print("Closing Window")
        self.close()


    def drop_source(self, widget, drag_context, x, y, time, data):
        print("DROPPED MMMEEE")
        self.stack.set_visible_child(self.icon)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.google_re = re.compile(
            "[http|https]:\/\/www.google.com\/imgres\?imgurl=(.*)\&imgrefurl"
        )
        self.button.hide()
        self.image_formats = ("image/png", "image/jpeg", "image/jpg")
        self.count = 0
        self.link_stack = []
        self.initial = 1
        self.stick()
        self.set_keep_above(True)
        if not os.path.exists('/tmp/pydrop'):
            os.mkdir("/tmp/pydrop")
        # drop destination stuff
        enforce_target = [
            Gtk.TargetEntry.new("application/octet-stream", Gtk.TargetFlags(4), 123),
            Gtk.TargetEntry.new("text/uri-list", Gtk.TargetFlags(4), TARGET_ENTRY_URI),
            
            Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags(4), TARGET_ENTRY_TEXT),
        ]

        self.droparea.drag_dest_set(
            Gtk.DestDefaults.ALL, enforce_target, Gdk.DragAction.COPY
        )
        self.droparea.connect("drag-data-received", self.on_drag_data_received)
        # self.droparea.connect("drag-motion", self.hello_source)
        self.droparea.connect("drag-drop", self.hello_source)

        # drag source stuff

        source_targets = [
            Gtk.TargetEntry.new("text/uri-list", Gtk.TargetFlags(4), TARGET_ENTRY_URI),
            Gtk.TargetEntry.new(
                "text/x-moz-url", Gtk.TargetFlags(4), TARGET_ENTRY_MOZ_URL
            ),
            Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags(4), TARGET_ENTRY_TEXT),
        ]

        self.button.drag_source_set(
            Gdk.ModifierType.BUTTON1_MASK, source_targets, Gdk.DragAction.COPY
        )
        self.button.connect("drag-begin", self.hello)
        self.button.connect("drag-data-get", self.on_drag_data_get)
        self.button.connect("drag-end", self.end)
