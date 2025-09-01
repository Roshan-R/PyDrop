from urllib.parse import unquote
from .utils import tools
from .dropped_item import DroppedItem
import re
import gi

gi.require_version("Soup", "3.0")
from gi.repository import Gdk, GObject, GLib, Soup  # noqa

google_re = re.compile(
    r"[http|https]:\/\/www.google.com\/imgres\?imgurl=(.*)\&imgrefurl"
)

BASE_DIR = GLib.get_user_cache_dir() + "/pydrop"
chunk_size = 4096


class ParseData(GObject.Object):
    def __init__(self, toggle_download_func):
        self.toggle_download_func = toggle_download_func
        self.soup = Soup.Session()
        super().__init__()

    def parse(self, value, dropped_items, count, callback):
        self.dropped_items = dropped_items
        self.callback = callback
        self.count = count

        match value:
            case Gdk.FileList():
                self.handle_file_list(value, callback)
            case Gdk.MemoryTexture():
                self.handle_memory_texture(value, callback)
            case str():
                # TODO: better count handling
                self.count += 1
                self.handle_text(value, callback)
            case _:
                print("Default", type(value), value)

    def handle_file_list(self, file_list: Gdk.FileList, callback):
        for file in file_list.get_files():
            # TODO: error handling if file path did not run correctly
            file_path = file.get_path()
            file_name = file.get_basename()
            self.dropped_items.append(DroppedItem(file_path, file_name))
            self.count += 1
            callback(self.count)

    def handle_memory_texture(self, memory_texture, callback):
        file_path = tools.generate_file_path(self.count, "png")
        memory_texture.save_to_png(file_path)
        paintable = memory_texture.get_current_image()
        self.dropped_items.append(DroppedItem(file_path, str(self.count), paintable))
        self.count += 1
        callback(self.count)

    def handle_text(self, text, callback):
        if tools.is_link(text):
            self.handle_link(text)
        else:
            self.write_to_text_file(text, callback)

    def write_to_text_file(self, text, callback):
        first_word = text.split()[0]
        file_path = tools.generate_file_path(first_word, "txt")
        with open(f"{file_path}", "w+") as f:
            f.write(text)
        self.dropped_items.append(DroppedItem(file_path, first_word))
        callback(self.count)

    def handle_link(self, link):
        self.link = link
        x = google_re.findall(self.link)
        if x:
            self.link = unquote(x[0])
            print("this is a google image : ", self.link)
            print("Google image link : ", self.link)
            # self.download_image(self.link, link_stack, count, callback)
            # TODO: check if this will work
            self.download_if_image_else_create_desktop_file()
        else:
            self.download_if_image_else_create_desktop_file()

    def download_if_image_else_create_desktop_file(
        self,
    ):
        self.message = Soup.Message.new("GET", self.link)
        self.message.get_request_headers().append(
            "User-Agent",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        self.soup.send_async(
            self.message, GLib.PRIORITY_DEFAULT, None, self.on_reponse_headers
        )

    def on_reponse_headers(self, session, task):
        # TODO: fail when the response is zero
        headers = self.message.get_response_headers()
        content_type, _ = headers.get_content_type()
        if content_type not in ["image/png", "image/jpeg", "image/jpg"]:
            self.handle_normal_link()
            return
        self.extension = content_type.split("/")[-1]
        input_stream = session.send_finish(task)
        self.toggle_download_func()
        buffer = bytearray()
        input_stream.read_bytes_async(
            chunk_size, GLib.PRIORITY_DEFAULT, None, self.on_read_callback, buffer
        )

    def on_read_callback(self, input_stream, task, buffer):
        data = input_stream.read_bytes_finish(task)
        if data.get_size():
            buffer.extend(data.get_data())
            input_stream.read_bytes_async(
                chunk_size, GLib.PRIORITY_DEFAULT, None, self.on_read_callback, buffer
            )
        else:
            file_path = tools.generate_file_path(self.count, self.extension)
            with open(file_path, "wb") as f:
                f.write(bytes(buffer))
            # TODO: generate paintable from here itself
            self.dropped_items.append(DroppedItem(file_path, str(self.count)))
            self.toggle_download_func()
            self.callback(self.count)

    def handle_normal_link(self):
        file_path = f"{BASE_DIR}/{self.count}.desktop"
        with open(file_path, "w+") as f:
            f.write(tools.get_desktop(self.link))
            self.dropped_items.append(
                DroppedItem(file_path, str(self.count) + ".desktop")
            )
        mime = "text/html"
        self.callback(self.count, mime)
