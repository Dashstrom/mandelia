from setuptools.extension import Extension
from sys import stderr

import numpy as np
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from setuptools import setup, find_packages


def read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"warning: No {path!r} found", file=stderr)
        return ""


include_dirs: list = [np.get_include()]
library_dirs: list = []
libraries: list = []

ext = cythonize([
    Extension(
        "*",
        ["mandelbrot/model/*.pyx"],
        libraries=libraries,
        extra_compile_args=["/openmp"],
        # extra_link_args=['/openmp'],
        include_dirs=include_dirs,
        library_dirs=library_dirs
    )],
    annotate=True,
    language_level=3,
    build_dir="mandelbrot/model"
)

setup(
    name='mandelbrot',
    version="1.0.1",
    author="***REMOVED*** ***REMOVED***",
    author_email='***REMOVED***.***REMOVED***@gmail.com',
    url='https://github.com/Dashstrom/raspinel',
    license=read("LICENSE"),
    packages=find_packages(exclude=('tests', 'docs')),
    long_description=read("README.md"),
    description=('Application to visualize '
                 'the fractal of mandelbrot and julia.'),
    cmdclass={'build_ext': build_ext},
    ext_modules=ext
)
