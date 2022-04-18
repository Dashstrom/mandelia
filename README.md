# ![Logo](https://raw.githubusercontent.com/Dashstrom/mandelia/main/docs/images/logo.png) Mandelia

[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
[![macOS](https://svgshare.com/i/ZjP.svg)](https://svgshare.com/i/ZjP.svg)
[![Windows](https://svgshare.com/i/ZhY.svg)](https://svgshare.com/i/ZhY.svg)

Application to visualize the fractal of mandelbrot and julia.

## Installation from PyPI

```sh
pip install mandelia
python -m mandelia
```

## Get Latest from Github

```sh
pip install git+https://github.com/Dashstrom/mandelia
```

## Standalone for Windows

Before trying to build, you need to install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

```sh
git clone https://github.com/Dashstrom/mandelia.git
cd mandelia
py setup.py exe
.\dist\Mandelia.exe
```

## Build Wheels locally

```sh
pip install cibuildwheel==2.4.0
cibuildwheel --platform windows
cibuildwheel --platform macos
cibuildwheel --platform linux
```

## Preview

### Main window

![Main Window](https://raw.githubusercontent.com/Dashstrom/mandelia/main/docs/images/main.png)

### Export Window

![Export Window](https://raw.githubusercontent.com/Dashstrom/mandelia/main/docs/images/export.png)

### Operation Window

![Operation Window](https://raw.githubusercontent.com/Dashstrom/mandelia/main/docs/images/operation.png)

## Languages

![Python](https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white)
![Cython](https://img.shields.io/badge/cython-f6c93d?style=for-the-badge&logo=python&logoColor=black)
