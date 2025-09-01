import gi

gi.require_version("Gtk", "4.0")  # noqa
gi.require_version("Gdk", "4.0")  # noqa

from gi.repository import Gio, Gdk, GObject
from .utils.tools import get_paintable_from_gicon, pixbuf_size
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository.Gdk import Texture


class DroppedItem(GObject.Object):
    def __init__(
        self,
        file_path: str,
        file_name: str,
        paintable: None | Gdk.Paintable = None,
        mime_type: str | None = None,
    ):
        self.file_path = file_path
        self.file_name = file_name
        if paintable:
            self.paintable = paintable
        else:
            if mime_type:
                self.mime_type = mime_type
                self.generate_paintable_from_mimetype()
            else:
                self.generate_paintable_from_file_path()

        super().__init__()

    def generate_paintable_from_mimetype(self):
        icon = Gio.content_type_get_icon(self.mime_type)
        self.paintable = get_paintable_from_gicon(icon)

    def generate_paintable_from_file_path(self):
        file = Gio.File.new_for_path(self.file_path)
        info = file.query_info(
            ",".join(
                [
                    Gio.FILE_ATTRIBUTE_STANDARD_ICON,
                    Gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE,
                ]
            ),
            Gio.FileQueryInfoFlags.NONE,
            None,
        )
        content_type = info.get_content_type()

        # TODO: does not work in case of some files, like psd
        # Create a fallback icon
        if content_type.split("/")[0] == "image":
            pixbuf = Pixbuf.new_from_file_at_scale(
                self.file_path, pixbuf_size, pixbuf_size, True
            )
            texture = Texture.new_for_pixbuf(pixbuf)
            self.paintable = texture.get_current_image()
        else:
            icon = info.get_attribute_object(Gio.FILE_ATTRIBUTE_STANDARD_ICON)
            self.paintable = get_paintable_from_gicon(icon)
