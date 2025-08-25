from urllib.parse import unquote
from .utils import tools
import re
import gi

gi.require_version("Soup", "3.0")
from gi.repository import Gdk, GObject, GLib, Soup, Gio

google_re = re.compile(
    r"[http|https]:\/\/www.google.com\/imgres\?imgurl=(.*)\&imgrefurl"
)

BASE_DIR = GLib.get_user_cache_dir() + "/pydrop"


class ParseData(GObject.Object):
    def __init__(self, toggle_download_func):
        self.toggle_download_func = toggle_download_func
        self.soup = Soup.Session()
        super().__init__()

    def parse(self, value, link_stack, count, callback):
        self.link_stack = link_stack
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
            self.link_stack.append(file.get_path())
            self.count += 1
            callback(self.count)

    def handle_memory_texture(self, memory_texture, callback):
        file_path = tools.generate_file_path(self.count, "png")
        memory_texture.save_to_png(file_path)
        self.link_stack.append(file_path)
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
        self.link_stack.append(file_path)
        callback(self.count)

    def handle_link(self, link):
        self.link = link
        x = google_re.findall(self.link)
        if x:
            self.link = unquote(x[0])
            print("this is a google image : ", self.link)
            print("Google image link : ", self.link)
            self.download_image(self.link, link_stack, count, callback)
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
        self.soup.send_async(self.message, 1, None, self.on_reponse_headers)

    def on_reponse_headers(self, session, task):
        # TODO: fail when the response is zero
        headers = self.message.get_response_headers()
        content_type, _ = headers.get_content_type()
        print(content_type)
        if content_type in ["image/png", "image/jpeg", "image/jpg"]:
            self.extension = content_type.split("/")[-1]
            self.download_image()
        else:
            self.handle_normal_link()

    def download_image(self):
        # TODO: make the download another thread
        self.toggle_download_func()
        print("Starting download...", self.link)
        self.message = Soup.Message.new("GET", self.link)
        self.message.get_request_headers().append(
            "User-Agent",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        self.soup.send_and_read_async(self.message, 1, None, self.on_response)

    def on_response(self, session, task):
        if self.message.get_status() != 200:
            # Do something when the request failed
            pass
        data = session.send_and_read_finish(task)
        file_path = tools.generate_file_path(self.count, self.extension)
        with open(file_path, "wb") as f:
            f.write(data.get_data())
        print("Finished download")
        self.link_stack.append(file_path)
        self.toggle_download_func()
        self.callback(self.count)

    def handle_normal_link(self):
        file_path = f"{BASE_DIR}/{self.count}.desktop"
        with open(file_path, "w+") as f:
            f.write(tools.get_desktop(self.link))
            self.link_stack.append(file_path)
        mime = "text/html"
        self.callback(self.count, mime)
