# ![Logo](https://raw.githubusercontent.com/Dashstrom/mandelia/main/docs/images/logo.png) Mandelia

![Build result](https://github.com/Dashstrom/mandelia/actions/workflows/build_and_publish.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/mandelia.svg)](https://badge.fury.io/py/mandelia)

[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
[![macOS](https://svgshare.com/i/ZjP.svg)](https://svgshare.com/i/ZjP.svg)
[![Windows](https://svgshare.com/i/ZhY.svg)](https://svgshare.com/i/ZhY.svg)

Application to visualize fractals of mandelbrot and julia.

## Installation from PyPI

```sh
pip3 install mandelia
python3 -m mandelia
```

## Get Latest from Github

Before trying to build, you need to install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

```sh
pip3 install git+https://github.com/Dashstrom/mandelia
python3 -m mandelia
```

## Install for developpement

```sh
git clone https://github.com/Dashstrom/mandelia.git
pip3 install -r requirements_dev.txt
python3 setup.py test
python3 -m mandelia
```

## Standalone for Windows

```sh
git clone https://github.com/Dashstrom/mandelia.git
cd mandelia
py setup.py exe
.\dist\Mandelia.exe
```

## Preview

### Main window

![Main Window](https://raw.githubusercontent.com/Dashstrom/mandelia/main/docs/images/main.png)

### Export Window

![Export Window](https://raw.githubusercontent.com/Dashstrom/mandelia/main/docs/images/export.png)

### Operation Window

![Operation Window](https://raw.githubusercontent.com/Dashstrom/mandelia/main/docs/images/operation.png)

## Languages

[![Python](https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Cython](https://img.shields.io/badge/cython-f6c93d?style=for-the-badge&logo=python&logoColor=black)](https://cython.org/)
