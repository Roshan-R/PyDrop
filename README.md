<h1 align="center">
  <img src="data/logo/com.github.Roshan_R.PyDrop.svg" alt="PyDrop" width="192" height="192"/><br>
  PyDrop
</h1>

<p align="center"><strong>A free and opensource alternative to Dropover</strong></p>

<p align="center">
  <a href="https://github.com/Roshan-R/PyDrop/actions/workflows/main.yml">
    <img src="https://github.com/Roshan-R/PyDrop/actions/workflows/main.yml/badge.svg" alt="CI status">
  </a>
</p>

<p align="center">
  <img src="https://github.com/Roshan-R/PyDrop/blob/main/screenshots/screenshot.png?raw=true" width="650" alt="Preview"/>
</p>

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
