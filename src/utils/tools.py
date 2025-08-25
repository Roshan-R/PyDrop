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
        info = file.query_info(
            Gio.FILE_ATTRIBUTE_STANDARD_ICON, Gio.FileQueryInfoFlags.NONE, None
        )
        if info:
            icon = info.get_attribute_object(Gio.FILE_ATTRIBUTE_STANDARD_ICON)
            return icon
    except Exception as e:
        print(f"Error getting icon for {filepath}: {e}")
    return None


def set_image(link_stack, image_widget, mime_type=None):
    """
    Sets the image or icon on the provided image widget.

    If a MIME type is specified, the corresponding icon for that MIME type is
    used.

    Otherwise, the function attempts to load the image at the top of the link
    stack using GdkPixbuf. If that fails (e.g. the file is not a supported
    image), it queries the file's information and derives an appropriate icon
    using the helper function `get_file_icon()`, which inspects the file
    metadata to choose a suitable icon.
    """
    if mime_type:
        image_widget.set_from_gicon(Gio.content_type_get_icon(mime_type))
        return
    file_path = unquote(link_stack[-1])
    try:
        pixbuf = Pixbuf.new_from_file_at_scale(
            file_path, pixbuf_size, pixbuf_size, True
        )
        image_widget.set_from_pixbuf(pixbuf)
    # TODO: get the file info and then do this instead of an exception.
    # i.e merge the two funcs
    except GError:
        icon = get_file_icon(file_path)
        image_widget.set_from_gicon(icon)


def generate_file_path(count, extension):
    BASE_DIR = GLib.get_user_cache_dir() + "/pydrop"
    return f"{BASE_DIR}/{count}.{extension}"
