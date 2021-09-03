import validators
import requests
import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio , Gtk

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
