# PyDrop
A free and opensource alternative to Dropover


## Building

### GNOME Builder

Download GNOME Builder.

In Builder, click the "Clone Repository" button at the bottom, using `https://github.com/Roshan-R/PyDrop` as the URL.

Click the build button at the top once the project is loaded.

### Building from Git

```bash
git clone https://github.com/Roshan-R/PyDrop.git
cd PyDrop
meson builddir --prefix=/usr/local
sudo ninja -C builddir install
```
