import shutil
import os
import glob
import re
import multiprocessing
from distutils.command.clean import clean
from typing import List
from sys import stderr

import numpy as np
from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext


class BuildExtCommand(build_ext):

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.inplace = 1


class EXECommand(BuildExtCommand):
    """A custom command to build an executable file."""

    description = "Build an executable"
    user_options: List[str] = []

    def finalize_options(self):
        BuildExtCommand.finalize_options(self)

    def initialize_options(self):
        BuildExtCommand.initialize_options(self)

    def run(self):
        """Run command."""
        BuildExtCommand.run(self)

        import PyInstaller.__main__

        PyInstaller.__main__.run([
            "--noconfirm",
            "--log-level=DEBUG",
            "--onefile",
            "--clean",
            "mandelia.spec"
        ])


class CleanCommand(clean):
    def run(self):
        clean.run(self)
        shutil.rmtree("dist", ignore_errors=True)
        shutil.rmtree("build", ignore_errors=True)
        for path in glob.glob("mandelia/model/fractale.*.pyd"):
            os.remove(path)
        for path in glob.glob("mandelia/model/fractale.*.so"):
            os.remove(path)


def read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"warning: No {path!r} found", file=stderr)
        return ""


def version() -> str:
    match = re.search(r"__version__ = \"(.+)\"", read("mandelia/__init__.py"))
    if match:
        return match.group(1)
    else:
        return "1.0.0"


include_dirs: list = [np.get_include()]
library_dirs: list = []
libraries: list = []

if os.name == "nt":
    extra_compile_args = extra_link_args = ["/openmp"]
else:
    extra_compile_args = extra_link_args = ["-fopenmp"]

ext = cythonize([
    Extension(
        "*",
        ["mandelia/model/*.pyx"],
        libraries=libraries,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        include_dirs=include_dirs,
        library_dirs=library_dirs
    )],
    nthreads=multiprocessing.cpu_count(),
    annotate=True,
    language_level=3,
    build_dir="build"
)

setup(
    name='mandelia',
    version=version(),
    author="Dashstrom",
    url='https://github.com/Dashstrom/mandelia',
    license="GPL-3.0 License",
    packages=find_packages(exclude=('tests', 'docs', '.github')),
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    description=('Application to visualize '
                 'the fractal of Mandelbrot and julia.'),
    cmdclass={
        'build_ext': BuildExtCommand,
        'exe': EXECommand,
        'clean': CleanCommand
    },
    ext_modules=ext,
    platforms=["Linux", "Windows"],
    package_data={
        "mandelia": ["view/images/*"],
    },
    install_requires=read("requirements.txt").split(),
    zip_safe=False
)
