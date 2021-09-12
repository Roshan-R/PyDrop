import validators
import requests
import os
from urllib.parse import unquote

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio , Gtk
from gi.repository.GdkPixbuf import Pixbuf, PixbufLoader

def link_is_image(link):
   """"
       returns True is link is an image
       else False

       https://stackoverflow.com/questions/10543940/check-if-a-url-to-an-image-is-up-and-exists-in-python
   """
   link = link.strip()
   image_formats = ["image/png", "image/jpeg", "image/jpg"]
   r = requests.head(link)
   if r.headers["content-type"] in image_formats:
       return True
   return False

def is_link(text):
    return validators.url(text)

def get_thumbnail(filename,size):
    """
    returns path to a valid icon file

    https://stackoverflow.com/questions/9203251/how-can-i-get-an-icon-or-thumbnail-for-a-specific-file/9212476
    """
    final_filename = ""
    if os.path.exists(filename):
        file = Gio.File.new_for_path(filename)
        info = file.query_info('standard::icon' , 0 , Gio.Cancellable())
        icon = info.get_icon().get_names()[0]

        icon_theme = Gtk.IconTheme.get_default()
        icon_file = icon_theme.lookup_icon(icon , size , 0)
        if icon_file != None:
            final_filename = icon_file.get_filename()
        return final_filename

def get_desktop(link):
    return f"[Desktop Entry]\nEncoding=UTF-8\nType=Link\nURL={link}\nIcon=text-html"

pixbuf_size = 80

def set_image(link_stack, icon, a):
    file_path = unquote(link_stack[-1][7:])
    icon_path = get_thumbnail(file_path, 512)
    print(file_path, icon_path, a)
    if not icon_path:
        print("Did not get themed icon")
        if "image" in a:
            print("Got image")
            try:
                pixbuf = Pixbuf.new_from_file_at_scale(file_path, pixbuf_size, pixbuf_size, True)
                icon.set_from_pixbuf(pixbuf)
            except :
                icon.set_from_gicon(Gio.content_type_get_icon(a), 512)
        else:
            gicon = Gio.content_type_get_icon(a)
            icon.set_from_gicon(gicon, 512)
    else:
        print("Normal")
        pixbuf = Pixbuf.new_from_file_at_scale(icon_path, pixbuf_size, pixbuf_size, True)
        icon.set_from_pixbuf(pixbuf)

def download_image(link, link_stack, count):

    # TODO: make the download another thread

    print(link)
    print("Starting download...")
    r = requests.get(link)

    extension = r.headers["content-type"].split('/')[1]
    file_path = f"/tmp/pydrop/{count}.{extension}"

    with open(file_path, "wb") as f:
        f.write(r.content)
    link_stack.append(f"file://{file_path}")
