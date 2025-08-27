import validators
import gi

gi.require_version("Gtk", "4.0")  # noqa
from gi.repository import Gtk, Gdk, GLib, Gsk  # noqa
from gi.repository.Graphene import Point


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


def create_overlayed_paintable(dropped_items):
    # FIXME: normal images get stretched
    width, height = pixbuf_size, pixbuf_size
    snapshot = Gtk.Snapshot.new()
    shadow = Gsk.Shadow()
    shadow.color = Gdk.RGBA(0, 0, 0, 0.4)  # semi-transparent black
    shadow.dx = 2
    shadow.dy = 2
    shadow.radius = 6

    items_count = len(dropped_items)
    snapshot.push_shadow([shadow])

    # TODO: document how this variable came to
    rotation_iterable = iter(range((items_count - 1) * 2, -1, -2))
    for index, dropped_item in enumerate(dropped_items):
        paintable = dropped_item.paintable
        width = paintable.get_intrinsic_width()
        height = paintable.get_intrinsic_height()

        # Rotate the paintable
        rotation_value = -1 * next(rotation_iterable)
        snapshot.save()
        snapshot.translate(Point().alloc().init(75, 75))
        snapshot.rotate(rotation_value)
        snapshot.translate(Point().alloc().init(-75, -75))
        paintable.snapshot(snapshot, width, height)
        snapshot.restore()

    # Remove the shadow related thing
    snapshot.pop()
    return snapshot.to_paintable()


def set_image(dropped_items, image_widget, mime_type=None):
    """
    Sets an appropriate image or icon on the provided image widget based on
    the MIME type or file content.
    """
    final_paintable = create_overlayed_paintable(dropped_items)
    image_widget.set_from_paintable(final_paintable)


def generate_file_path(count, extension):
    BASE_DIR = GLib.get_user_cache_dir() + "/pydrop"
    return f"{BASE_DIR}/{count}.{extension}"
