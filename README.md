# PyDrop
A free and opensource alternative to Dropover

![screenshot](https://user-images.githubusercontent.com/43182697/131822069-7729c131-b019-408e-a5fd-0ff724e2589d.png)

Use [releases](https://github.com/Roshan-R/PyDrop/releases) for installing a beta version


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
