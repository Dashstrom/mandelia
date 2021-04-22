from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext

# py setup.py build_ext --inplace
# annotate=True pour l'html

extensions = [
    Extension("fractale", ["mandelbrot/fractale.pyx"])
]

setup(
    cmdclass={'build_ext': build_ext},
    ext_modules=cythonize(extensions, annotate=True, language_level=3)
)
