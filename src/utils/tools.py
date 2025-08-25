import validators
from urllib.parse import unquote
import gi

gi.require_version("Gtk", "4.0")  # noqa
from gi.repository import Gio, Gtk, Gdk, GLib  # noqa
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository.GLib import GError


# Instead of hardcoding the value, get it from the image_widget
pixbuf_size = 150


def is_link(text):
    return validators.url(text)


def get_paintable_from_gicon(gicon):
    display = Gdk.Display.get_default()
    icon_theme = Gtk.IconTheme.get_for_display(display)
    paintable = icon_theme.lookup_by_gicon(
        gicon, 150, 1, Gtk.TextDirection.NONE, Gtk.IconLookupFlags.NONE
    )
    return paintable


def get_desktop(link):
    return f"[Desktop Entry]\nEncoding=UTF-8\nType=Link\nURL={link}\nIcon=text-html"


def set_image(link_stack, image_widget, mime_type=None):
    """
    Sets an appropriate image or icon on the provided image widget based on
    the MIME type or file content.
    """
    if mime_type:
        image_widget.set_from_gicon(Gio.content_type_get_icon(mime_type))
        return
    file_path = unquote(link_stack[-1])
    file = Gio.File.new_for_path(file_path)
    info = file.query_info(
        ",".join(
            [Gio.FILE_ATTRIBUTE_STANDARD_ICON, Gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE]
        ),
        Gio.FileQueryInfoFlags.NONE,
        None,
    )
    content_type = info.get_content_type()
    if content_type.split("/")[0] == "image":
        pixbuf = Pixbuf.new_from_file_at_scale(
            file_path, pixbuf_size, pixbuf_size, True
        )
        image_widget.set_from_pixbuf(pixbuf)
    else:
        icon = info.get_attribute_object(Gio.FILE_ATTRIBUTE_STANDARD_ICON)
        image_widget.set_from_gicon(icon)


def generate_file_path(count, extension):
    BASE_DIR = GLib.get_user_cache_dir() + "/pydrop"
    return f"{BASE_DIR}/{count}.{extension}"
