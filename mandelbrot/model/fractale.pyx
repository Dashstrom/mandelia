# distutils: language=c++

import numpy as np
import struct as s

from PIL import Image

cimport numpy as np
cimport cython

from cython.parallel import prange

DTYPE = np.uint32
ctypedef np.uint32_t DTYPE_t

COLORTYPE = np.uint8
ctypedef np.uint8_t COLORTYPE_t

DEF PIXEL_DEFAULT = 0.02
DEF MIN_PIXEL_SIZE = PIXEL_DEFAULT * 16


cdef unsigned int iterate(double z_r, double z_i, double c_r, double c_i,
                          unsigned int iterations) nogil except +:
    """
    Iterate on a complex numbers.
    formula: Zn+1 = Zn ** 2 + C
    """
    cdef:
        double tmp
        unsigned int i

    for i in range(iterations):
        tmp = z_r
        z_r = z_r * z_r - z_i * z_i + c_r
        z_i = 2 * z_i * tmp + c_i
        if z_r * z_r + z_i * z_i > 4:
            break
    return 0 if i == iterations - 1 else i + 1


modulo_coloration_saver = s.Struct("BBB")
cdef class ModuloColoration:
    cdef:
        public unsigned char r, g, b

    def __init__(self, r, g, b):
        self.r, self.g, self.b = r, g, b

    cpdef to_bytes(self):
        """Convert ModuloColor into bytes."""
        return modulo_coloration_saver.pack(self.r, self.g, self.b)

    cpdef from_bytes(self, bytes bytes_):
        """Convert bytes into ModuloColor."""
        self.r, self.g, self.b = modulo_coloration_saver.unpack(bytes_)

    cpdef bytes_size(self):
        return modulo_coloration_saver.size

    @cython.boundscheck(False)  # turn off bounds-checking
    @cython.wraparound(False)  # turn off negative index wrapping
    cpdef np.ndarray[COLORTYPE_t, ndim=3] colorize(
            self, np.ndarray[DTYPE_t, ndim=2] np_fractale):
        """ColorInteraction a two-dimensional array."""
        cdef:
            short width, height, x, y
            unsigned char r = self.r, g = self.g, b = self.b
            unsigned int i
            np.ndarray[COLORTYPE_t, ndim=3] image

        width = np_fractale.shape[0]
        height = np_fractale.shape[1]
        image = np.zeros((height, width, 3), dtype=COLORTYPE)
        for x in prange(width, schedule='guided', nogil=True):
            for y in range(height):
                i = np_fractale[x, y]
                if i != 0:
                    image[y, x, 0] = r * i
                    image[y, x, 1] = g * i
                    image[y, x, 2] = b * i
        return image

fractale_saver = s.Struct("dddhhI")
cdef class Fractale:
    cdef:
        readonly double real, imaginary, pixel_size
        readonly short width, height
        readonly unsigned int iterations
        readonly need_update
        content
        ModuloColoration color

    def __init__(self, ModuloColoration color, real=0, imaginary=0,
                 iterations=1_000, width=48, height=48,
                 pixel_size=PIXEL_DEFAULT):
        self.content = np.zeros((width, height), dtype=DTYPE)
        self.color = color
        self.real = real
        self.imaginary = imaginary
        self.iterations = iterations
        self.width = width
        self.height = height
        self.pixel_size = pixel_size
        self.need_update = True

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (f"<{self.__class__.__name__} "
                f"pixel_size={self.pixel_size} "
                f"{self.real}{self.imaginary:+}i>")

    cpdef set_real(self, double real):
        """Set real part of Z."""
        self.real = real
        self.need_update = True

    cpdef set_imaginary(self, double imaginary):
        """Set imaginary part of Z."""
        self.imaginary = imaginary
        self.need_update = True

    cpdef set_iterations(self, unsigned int iterations):
        """Set max iterations."""
        self.iterations = iterations

    cpdef resize(self, short width, short height):
        """Resize width and height, and adjust the zoom if necessary."""
        cdef double multiplier
        multiplier = width / self.width
        self.width = width
        self.height = height
        self.middle_zoom(multiplier)
        self.need_update = True

    cpdef iterations_sum(self):
        """Total number of iterations."""
        cdef unsigned long long sum_
        sum_ = np.sum(self.content)
        sum_ += np.count_nonzero(self.content == 0) * self.iterations
        return sum_

    cpdef iterations_per_pixel(self):
        """Average iteration per pixel."""
        cdef unsigned int pixels
        pixels = self.width * self.height
        return self.iterations_sum() / pixels if pixels != 0 else 0

    cdef _check_min_size(self):
        """Increases pixel size if it is smaller than MIN_PIXEL_SIZE."""
        cdef double multiplier = self.pixel_size / MIN_PIXEL_SIZE
        if self.pixel_size > MIN_PIXEL_SIZE:
            self.pixel_size = MIN_PIXEL_SIZE
            self.real = self.real / multiplier
            self.imaginary = self.imaginary / multiplier
            if -0.001 < self.real < 0.001:
                self.real = 0
            if -0.001 < self.imaginary < 0.001:
                self.imaginary = 0

    cpdef image(self):
        """
        Compute image if there is update otherwise just do the coloring.
        """
        cdef np.ndarray[COLORTYPE_t, ndim=3] colored
        if self.need_update:
            self._compute()
            self.need_update = False
        colored = self.color.colorize(self.content)
        return Image.fromarray(colored, 'RGB')

    cpdef image_at_size(self, short width, short height):
        """
        Get image with specific size.
        """
        cdef:
            np.ndarray[DTYPE_t, ndim=2] content_copy
            short x
            short w_copy = self.width
            short h_copy = self.height
            double real_copy = self.real
            double imaginary_copy = self.imaginary
            double pixel_copy = self.pixel_size

        if w_copy != width or h_copy != height:
            content_copy = self.content.copy()
            self.resize(width, height)
            img = self.image()
            self.real = real_copy
            self.imaginary = imaginary_copy
            self.pixel_size = pixel_copy
            self.content = content_copy
            self.width = w_copy
            self.height = h_copy
        else:
            img = self.image()
        return img

    cpdef top(self):
        """Set pixel at default size."""
        if self.pixel_size != PIXEL_DEFAULT:
            self.pixel_size = PIXEL_DEFAULT
            self.need_update = True

    cpdef middle_zoom(self, double multiplier):
        """Zoom at the middle."""
        self.zoom(self.width // 2, self.height // 2, multiplier)

    cpdef zoom(self, short x, short y, double multiplier):
        """Zoom at a position in the image."""
        cdef double pixel = self.pixel_size, real = self.real, imaginary = self.imaginary
        self.real = (real * 1 / multiplier
                     + (real + x * pixel - self.width / 2 * pixel)
                     * (1 - 1 / multiplier))
        self.imaginary = (imaginary * 1 / multiplier
                          + (imaginary + y * pixel - self.height / 2 * pixel)
                          * (1 - 1 / multiplier))
        self.pixel_size /= multiplier
        self._check_min_size()
        self.need_update = True

    cpdef reset(self):
        """Reset position and pixel size."""
        self.real = 0
        self.imaginary = 0
        self.pixel_size = PIXEL_DEFAULT
        self.need_update = True

    cdef np.ndarray[DTYPE_t, ndim=2] _compute(self):
        """Compute fractale."""
        raise NotImplementedError()

    cpdef real_at_x(self, short x):
        """Return real part of Z at x in image."""
        cdef double start_r = self.real - (self.width * self.pixel_size) / 2
        return start_r + x * self.pixel_size

    cpdef imaginary_at_y(self, short y):
        """Return imaginary part of Z at y in image."""
        cdef double start_i = self.imaginary - (
                self.height * self.pixel_size) / 2
        return start_i + y * self.pixel_size

    cpdef to_bytes(self):
        """Return bytes representative of the fractal."""
        data = fractale_saver.pack(
            self.real,
            self.imaginary,
            self.pixel_size,
            self.width,
            self.height,
            self.iterations
        )
        data += self.color.to_bytes()
        return data

    cpdef from_bytes(self, bytes bytes_):
        """Load data on the fractal."""
        cdef short w = self.width, h = self.height
        record = fractale_saver.unpack(bytes_[:32])
        (self.real, self.imaginary, self.pixel_size,
            self.width, self.height, self.iterations) = record
        self.resize(w, h)
        self.color.from_bytes(bytes_[32:])
        self.need_update = True

    cpdef bytes_size(self):
        return fractale_saver.size + self.color.bytes_size()


julia_saver = s.Struct("dd")
cdef class Julia(Fractale):
    cdef:
        readonly double c_r, c_i
    def __init__(self, color: ModuloColoration, c_r=0, c_i=0, real=0,
                 imaginary=0, iterations=1_000, width=48, height=48,
                 pixel_size=PIXEL_DEFAULT):
        self.c_r = c_r
        self.c_i = c_i
        super().__init__(color, real, imaginary, iterations, width,
                         height, pixel_size)

    cpdef set_c_r(self, double c_r):
        """Set real part of C."""
        self.c_r = c_r
        self.need_update = True

    cpdef set_c_i(self, double c_i):
        """Set imaginary part of C."""
        self.c_i = c_i
        self.need_update = True

    cpdef to_bytes(self):
        """Return bytes representative of the fractal."""
        return (super(Julia, self).to_bytes()
                + julia_saver.pack(self.c_r, self.c_i))

    cpdef from_bytes(self, bytes bytes_):
        """Load data on the fractal."""
        super(Julia, self).from_bytes(bytes_[:-16])
        self.c_r, self.c_i = julia_saver.unpack(bytes_[-16:])

    cpdef bytes_size(self):
        return super(Julia, self).bytes_size() + julia_saver.size

    @cython.boundscheck(False)  # turn off bounds-checking
    @cython.wraparound(False)  # turn off negative index wrapping
    cdef np.ndarray[DTYPE_t, ndim=2] _compute(self):
        """Compute fractal."""
        cdef:
            double z_r, z_i, tmp, x_start, y_start
            double real = self.real
            double imaginary = self.imaginary
            double pixel_size = self.pixel_size
            double c_r = self.c_r
            double c_i = self.c_i
            short width = self.width, height = self.height
            short y, x
            unsigned int i, iterations = self.iterations
            np.ndarray[DTYPE_t, ndim=2] content = np.zeros((width, height),
                                                           dtype=DTYPE)
        x_start = real - (width >> 1) * pixel_size
        y_start = imaginary - (height >> 1) * pixel_size
        for x in prange(width, schedule='guided', nogil=True):
            z_r = x_start + x * pixel_size
            for y in range(height):
                z_i = y_start + y * pixel_size
                content[x, y] = iterate(z_r, z_i, c_r, c_i, iterations)
        self.content = content


cdef class Mandelbrot(Fractale):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cython.boundscheck(False)  # turn off bounds-checking
    @cython.wraparound(False)  # turn off negative index wrapping
    cdef np.ndarray[DTYPE_t, ndim=2] _compute(self):
        """Compute mandelbrot fractale."""
        cdef:
            double c_r, c_i, z_r, z_i, tmp, x_start, y_start
            double real = self.real
            double imaginary = self.imaginary
            double pixel_size = self.pixel_size
            short y, x
            unsigned int i, iterations = self.iterations
            short width = self.width, height = self.height
            np.ndarray[DTYPE_t, ndim=2] content = np.zeros((width, height),
                                                           dtype=DTYPE)
        x_start = real - (width >> 1) * pixel_size
        y_start = imaginary - (height >> 1) * pixel_size
        for x in prange(width, schedule='guided', nogil=True):
            c_r = x_start + x * pixel_size
            for y in range(height):
                c_i = y_start + y * pixel_size
                content[x, y] = iterate(0, 0, c_r, c_i, iterations)
        self.content = content