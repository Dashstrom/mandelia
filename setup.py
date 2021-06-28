from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
import numpy as np

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
    language_level=3
)

setup(
    name='Fractale',
    author='Dashstrom',
    version='0.1',
    cmdclass={'build_ext': build_ext},
    ext_modules=ext
)
