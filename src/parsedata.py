(TARGET_OCTECT_STREAM, TARGET_PNG, TARGET_URI_LIST, TARGET_PLAIN) = range(4)


import magic
from urllib.parse import unquote
from .utils import tools
import re
from PIL import Image
import io

from gi.repository import Gtk, Gdk, Gio, Adw, GObject

google_re = re.compile(
    "[http|https]:\/\/www.google.com\/imgres\?imgurl=(.*)\&imgrefurl"
)


class ParseData:
    def parse(self, value, link_stack, count):
        match type(value):
            case Gdk.FileList:
                # print(type(value), [f.get_path() for f in value.get_files()])
                for file in value.get_files():
                    link_stack.append(file.get_path())
                    count += 1
                    mime = magic.Magic(mime=True)
                try:
                    a = mime.from_file(file.get_path())
                except IsADirectoryError:
                    a = "inode/directory"
                return count, a
            case str():
                print(type(value), value)
            case Gdk.MemoryTexture:
                print(type(value), value)
            case _:
                print("Default", type(value), value)

        # Application/Octect stream : Image from Chromuim browsers
        if value == TARGET_OCTECT_STREAM or value == TARGET_PNG:
            print("Got Image")
            image = Image.open(io.BytesIO(data.get_data()))
            format = image.format.lower()
            image.save(f"/tmp/pydrop/{count}.{format}")
            link_stack.append(f"file:///tmp/pydrop/{count}.{format}")
            count += 1
            a = "image"

        elif value == TARGET_PLAIN:
            text = data.get_text()
            print(text)

            if tools.is_link(text):
                link = text
                x = google_re.findall(link)
                if x:
                    link = unquote(x[0])
                    print("this is a google image : ", link)
                    print("Google image link : ", link)
                    tools.download_image(link, link_stack, count)
                    a = "image"

                elif tools.link_is_image(link):
                    tools.download_image(link.link_stack, count)
                    a = "image"
                else:
                    # TODO: handle link better, preferably make a file that contains the link?
                    # investigate on which filetype to use
                    file_path = f"/tmp/pydrop/{count}.desktop"
                    with open(file_path, "w+") as f:
                        f.write(tools.get_desktop(link))
                        link_stack.append(f"file://{file_path}")
                    a = "text/html"
            else:
                print("Got text")
                file_name = f"{text.split()[0]}.txt"
                file_path = f"/tmp/pydrop/{file_name}"
                with open(f"{file_path}", "w+") as f:
                    f.write(text)
                link_stack.append(f"file://{file_path}")
                a = "text/plain"

            count += 1
        return count, a
