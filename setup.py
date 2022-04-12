import shutil
import os
import sys
import glob
import re
import multiprocessing
from distutils.command.clean import clean

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
    user_options = []  # type: list[str]

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
        print(f"warning: No {path!r} found", file=sys.stderr)
        return ""


def version() -> str:
    match = re.search(r"__version__ = \"(.+)\"", read("mandelia/__init__.py"))
    if match:
        return match.group(1)
    else:
        return "1.0.0"


extra_compile_args = []  # type: list[str]
extra_link_args = []  # type: list[str]
include_dirs = [np.get_include()]  # type: list[str]
library_dirs = []  # type: list[str]
libraries = []  # type: list[str]
numpy_ver = "numpy"


if sys.platform.startswith("linux"):
    extra_compile_args += ["-fopenmp"]
    extra_link_args += []
elif sys.platform == "darwin":
    if sys.version_info <= (3, 7):
        numpy_ver = "numpy==1.18.0"
    os.environ["CC"] = "/usr/local/opt/llvm/bin/clang"
    os.environ["CXX"] = "/usr/local/opt/llvm/bin/clang++"
    extra_compile_args += ["-w", "-fopenmp", "-stdlib=libc++"]
    extra_link_args += ["-fopenmp", "-stdlib=libc++"]
    include_dirs += ["/usr/local/opt/llvm/include"]
    library_dirs += ["/usr/local/opt/llvm/lib"]
elif sys.platform == "win32":
    extra_compile_args += ["/openmp"]
    extra_link_args += []


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
    email="dashstrom.pro@gmail.com",
    url='https://github.com/Dashstrom/mandelia',
    license="GPL-3.0 License",
    packages=find_packages(exclude=('tests', 'docs', '.github')),
    long_description=read("README.md"),
    python_requires='>3.5.0',
    long_description_content_type="text/markdown",
    description=('Application to visualize '
                 'the fractal of Mandelbrot and julia.'),
    cmdclass={
        'build_ext': BuildExtCommand,
        'exe': EXECommand,
        'clean': CleanCommand
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: OS Independent",
        "Natural Language :: French"
    ],
    ext_modules=ext,
    platforms=['any'],
    package_data={
        "mandelia": ["view/images/*", "**/*.pyi", "**/*.pyx"],
    },
    keywords=["mandelbrot", "julia", "fractale", "tkinter"],
    install_requires=[
        "wheel",
        numpy_ver,
        "Cython",
        "future",
        "Pillow",
        "opencv-python",
        "PyInstaller",
        "Cython"
    ],
    entry_points={
        'console_scripts': [
            'mandelia=mandelia.__main__:main',
        ]
    },
    zip_safe=False
)
