import validators
import os
from urllib.parse import unquote

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, Gtk, Gdk, GLib
from gi.repository.GdkPixbuf import Pixbuf, PixbufLoader


def is_link(text):
    return validators.url(text)


# def get_thumbnail(filename):
#    """
#    returns path to a valid icon file
#
#    https://stackoverflow.com/questions/9203251/how-can-i-get-an-icon-or-thumbnail-for-a-specific-file/9212476
#    """
#    final_filename = ""
#    if os.path.exists(filename):
#        file = Gio.File.new_for_path(filename)
#        info = file.query_info("standard::icon", 0, Gio.Cancellable())
#        icon = info.get_icon().get_names()[0]
#        print("Icon is", icon)
#        display = Gdk.Display.get_default()
#        icon_theme = Gtk.IconTheme.get_for_display(display)
#        icon_file = icon_theme.lookup_icon(icon, 512, 0, Gtk.TextDirection.NONE, Gtk.IconLookupFlags.NONE, None)
#        if icon_file != None:
#            final_filename = icon_file.get_filename()
#        return final_filename


def get_paintable_from_gicon(gicon):
    display = Gdk.Display.get_default()
    icon_theme = Gtk.IconTheme.get_for_display(display)
    paintable = icon_theme.lookup_by_gicon(
        gicon, 24, 1, Gtk.TextDirection.NONE, Gtk.IconLookupFlags.NONE
    )
    return paintable


def get_desktop(link):
    return f"[Desktop Entry]\nEncoding=UTF-8\nType=Link\nURL={link}\nIcon=text-html"


pixbuf_size = 150


def new_set_image(link_stack: list, icon: Gtk.Widget):
    last_ele = link_stack[-1]

    pass

def get_file_icon(filepath):
    """
    Retrieves the standard icon for a given file path.

    Args:
        filepath (str): The path to the file.

    Returns:
        Gio.Icon or None: The GIcon object representing the file's icon,
                          or None if no icon can be retrieved.
    """
    try:
        file = Gio.File.new_for_path(filepath)
        # Query for the standard icon attribute
        info = file.query_info(Gio.FILE_ATTRIBUTE_STANDARD_ICON, Gio.FileQueryInfoFlags.NONE, None)
        if info:
            icon = info.get_attribute_object(Gio.FILE_ATTRIBUTE_STANDARD_ICON)
            return icon
    except Exception as e:
        print(f"Error getting icon for {filepath}: {e}")
    return None

def set_image(link_stack, image_widget, mime_type = None):
    if mime_type:
        image_widget.set_from_gicon(Gio.content_type_get_icon(mime_type))
        return
    file_path = unquote(link_stack[-1])
    # TODO: make use of themed icon for better consistency
    try:
        pixbuf = Pixbuf.new_from_file_at_scale(
            file_path, pixbuf_size, pixbuf_size, True
        )
        image_widget.set_from_pixbuf(pixbuf)
    except:
        icon = get_file_icon(file_path)
        image_widget.set_from_gicon(icon)
    # icon_path = None
    # icon_path = get_thumbnail(file_path)
    # print(file_path, icon_path, a)
    # if not icon_path:
    #    print("Did not get themed icon")
    #    if "image" in a:
    #        print("Got image")
    #        try:
    #            print("Trying to set it from pixbuf")
    #            pixbuf = Pixbuf.new_from_file_at_scale(
    #                file_path, pixbuf_size, pixbuf_size, True
    #            )
    #            icon.set_from_pixbuf(pixbuf)
    #        except e:
    #            print("Failed", e)
    #            print("Trying to set it from Gicon")
    #            icon.set_from_gicon(Gio.content_type_get_icon(a))
    #    else:
    #        gicon = Gio.content_type_get_icon(a)
    #        icon.set_from_gicon(gicon)
    # else:
    #    print("Normal")
    #    pixbuf = Pixbuf.new_from_file_at_scale(
    #        icon_path, pixbuf_size, pixbuf_size, True
    #    )
    #    icon.set_from_pixbuf(pixbuf)


def generate_file_path(count, extension):
    BASE_DIR = GLib.get_user_cache_dir() + "/pydrop"
    return f"{BASE_DIR}/{count}.{extension}"
