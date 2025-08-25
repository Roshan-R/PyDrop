(TARGET_OCTECT_STREAM, TARGET_PNG, TARGET_URI_LIST, TARGET_PLAIN) = range(4)


import magic
from urllib.parse import unquote
from .utils import tools
import re
from PIL import Image
import io
import gi

gi.require_version("Soup", "3.0")
from gi.repository import Gtk, Gdk, Gio, Adw, GObject, GLib, Soup

google_re = re.compile(
    r"[http|https]:\/\/www.google.com\/imgres\?imgurl=(.*)\&imgrefurl"
)

BASE_DIR = GLib.get_user_cache_dir() + "/pydrop"


class ParseData(GObject.Object):
    def __init__(self, toggle_download_func):
        self.toggle_download_func = toggle_download_func
        self.soup = Soup.Session()
        super().__init__()

    def download_image(self, link, link_stack, count, callback):
        # TODO: make the download another thread
        self.toggle_download_func()
        print("Starting download...", link)
        self.message = Soup.Message.new("GET", link)
        self.message.get_request_headers().append(
            "User-Agent",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        self.soup.send_and_read_async(
            self.message, 1, None, self.on_response, (link_stack, count, callback)
        )

    def on_response(self, session, task, params):
        link_stack, count, callback = params
        if self.message.get_status() != 200:
            # Do something when the request failed
            pass
        # get png from image/png
        headers = self.message.get_response_headers()
        extension = headers.get_content_type()[0].split("/")[-1]
        data = session.send_and_read_finish(task)
        file_path = tools.generate_file_path(count, extension)
        with open(file_path, "wb") as f:
            f.write(data.get_data())
        print("Finished download")
        link_stack.append(file_path)
        self.toggle_download_func()
        callback(count, "image")

    def parse(self, value, link_stack, count, callback):
        match value:
            case Gdk.FileList():
                # print(type(value), [f.get_path() for f in value.get_files()])
                for file in value.get_files():
                    link_stack.append(file.get_path())
                    count += 1
                    mime = magic.Magic(mime=True)
                try:
                    mime = mime.from_file(file.get_path())
                except IsADirectoryError:
                    mime = "inode/directory"
                callback(count, mime)
            case Gdk.MemoryTexture():
                file_name = BASE_DIR + f"/{count}.png"
                # TODO: make this faster for large files
                value.save_to_png(file_name)
                link_stack.append(file_name)
                count += 1
                mime = "image"
                callback(count, mime)
            case str():
                count += 1
                text = value
                if tools.is_link(text):
                    link = text
                    x = google_re.findall(link)
                    if x:
                        link = unquote(x[0])
                        print("this is a google image : ", link)
                        print("Google image link : ", link)
                        self.download_image(link, link_stack, count, callback)
                    elif tools.link_is_image(link):
                        print("The link is an image", link)
                        self.download_image(link, link_stack, count, callback)
                    else:
                        # TODO: handle link better, preferably make a file that contains the link?
                        # investigate on which filetype to use
                        file_path = f"{BASE_DIR}/{count}.desktop"
                        with open(file_path, "w+") as f:
                            f.write(tools.get_desktop(link))
                            link_stack.append(file_path)
                        mime = "text/html"
                        callback(count, mime)
                else:
                    print("Got text")
                    file_name = f"{text.split()[0]}.txt"
                    file_path = f"{BASE_DIR}/{file_name}"
                    with open(f"{file_path}", "w+") as f:
                        f.write(text)
                    link_stack.append(file_path)
                    mime = "text/plain"
                    callback(count, mime)
            case _:
                print("Default", type(value), value)
