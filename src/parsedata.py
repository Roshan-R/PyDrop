(TARGET_OCTECT_STREAM, TARGET_URI_LIST, TARGET_PLAIN) = range(3)

import magic
from urllib.parse import unquote
from .utils import tools
import re
from PIL import Image
import io

google_re = re.compile(
        "[http|https]:\/\/www.google.com\/imgres\?imgurl=(.*)\&imgrefurl"
        )

class ParseData:
    def parse(self, data, info, link_stack, count):

        if info == TARGET_URI_LIST:
            for uri in data.get_uris():
                link_stack.append(uri)
                count += 1
                mime = magic.Magic(mime=True)
            try:
                a = mime.from_file(unquote(uri[7:]))
            except IsADirectoryError:
                a = "inode/directory"

       # Application/Octect stream : Image from Chromuim browsers
        if info == TARGET_OCTECT_STREAM:
            print("Got Image from browser")
            image = Image.open(io.BytesIO(data.get_data()))
            format = image.format.lower()
            image.save(f"/tmp/pydrop/{count}.{format}")
            link_stack.append(f"file:///tmp/pydrop/{count}.{format}")
            count += 1
            a = "image"


        elif info == TARGET_PLAIN:

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
                    tools.download_image(link. link_stack, count)
                    a = "image"
                else:
                    # TODO: handle link better, preferably make a file that contains the link?
                    # investigate on which filetype to use
                    file_path = f'/tmp/pydrop/{count}.desktop'
                    with open(file_path, 'w+') as f:
                        f.write(tools.get_desktop(link))
                        link_stack.append(f'file://{file_path}')
                    a = "text/html"
            else:
                print("Got text")
                file_name = f'{text.split()[0]}.txt'
                file_path = f'/tmp/pydrop/{file_name}'
                with open(f'{file_path}', 'w+') as f:
                    f.write(text)
                link_stack.append(f'file://{file_path}')
                a = "text/plain"

            count += 1
        return count, a
