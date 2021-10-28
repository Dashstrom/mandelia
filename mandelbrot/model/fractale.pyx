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
DEF BASE_SAVE_SIZE = 48
DEF JULIA_SIZE = BASE_SAVE_SIZE + 16
DEF MANDELBROT_SIZE = BASE_SAVE_SIZE

cpdef check_bytes_size(bytes_, int size):
    """Check the count of bytes and type."""
    if not isinstance(bytes_, bytes):
        raise TypeError(f"bytes_ must be bytes type, got {type(bytes)}")
    elif len(bytes_) != size:
        raise ValueError(
            f"bytes_ must contain {size} bytes , got {len(bytes_)}")

cdef to_bytes(obj):
    """Convert numbers into bytes."""
    if isinstance(obj, int):
        return s.pack(">I", int(obj))
    elif isinstance(obj, float):
        return s.pack("d", float(obj))
    else:
        raise TypeError(f"{type(obj)} is not valid object for bytes")

cdef from_bytes(bytes_):
    """
    Convert bytes into numbers based on bytes length.
    
    8 for float and 4 for int.
    """
    if not isinstance(bytes_, bytes):
        raise TypeError("incorrect type")
    if len(bytes_) == 4:
        return s.unpack(">I", bytes_)[0]
    elif len(bytes_) == 8:
        return s.unpack("d", bytes_)[0]
    else:
        raise TypeError(
            f"bytes have invalid length is not valid object for bytes")

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

cdef class ModuloColoration:
    cdef public unsigned char r, g, b

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    cpdef to_bytes(self):
        """Convert ModuloColor into bytes."""
        return to_bytes(self.r) + to_bytes(self.g) + to_bytes(self.b)

    cpdef from_bytes(self, bytes bytes_):
        """Convert bytes into ModuloColor."""
        check_bytes_size(bytes_, 12)
        self.r = from_bytes(bytes_[0:4])
        self.g = from_bytes(bytes_[4:8])
        self.b = from_bytes(bytes_[8:12])

    @cython.boundscheck(False)  # turn off bounds-checking
    @cython.wraparound(False)  # turn off negative index wrapping
    cpdef np.ndarray[COLORTYPE_t, ndim=3] colorize(
            self, np.ndarray[DTYPE_t, ndim=2] np_fractale):
        """Color a two-dimensional array."""
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

cdef class Fractale:
    cdef:
        readonly double real, imaginary, pixel_size
        readonly short width, height
        readonly unsigned int iterations
        readonly need_update
        content
        ModuloColoration color

    def __init__(self, ModuloColoration color, real=0, imaginary=0,
                 iterations=1_000,
                 width=48, height=48, pixel_size=PIXEL_DEFAULT):
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
        return (to_bytes(self.real)
                + to_bytes(self.imaginary)
                + to_bytes(self.pixel_size)
                + to_bytes(self.width)
                + to_bytes(self.height)
                + to_bytes(self.iterations)
                + self.color.to_bytes())

    cpdef from_bytes(self, bytes bytes_):
        """Load data on the fractal."""
        cdef short w = self.width, h = self.height
        check_bytes_size(bytes_, 48)
        self.real = from_bytes(bytes_[0:8])
        self.imaginary = from_bytes(bytes_[8:16])
        self.pixel_size = from_bytes(bytes_[16:24])
        self.width = from_bytes(bytes_[24:28])
        self.height = from_bytes(bytes_[28:32])
        self.iterations = from_bytes(bytes_[32:36])
        self.color.from_bytes(bytes_[36:48])
        self.resize(w, h)
        self.need_update = True

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
                + to_bytes(self.c_r)
                + to_bytes(self.c_i))

    cpdef from_bytes(self, bytes bytes_):
        """Load data on the fractal."""
        morsel = bytes_[-16:]
        bytes_ = bytes_[:-16]
        check_bytes_size(morsel, 16)
        super(Julia, self).from_bytes(bytes_)
        self.c_r = from_bytes(morsel[:8])
        self.c_i = from_bytes(morsel[8:])

    @cython.boundscheck(False)  # turn off bounds-checking
    @cython.wraparound(False)  # turn off negative index wrapping
    cdef np.ndarray[DTYPE_t, ndim=2] _compute(self):
        """Compute fractal."""
        cdef:
            double z_r, z_i, pre_z_r, tmp, x_start, y_start, ld_y, ld_x
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
        x_start = real - width / 2 * pixel_size
        y_start = imaginary - height / 2 * pixel_size
        for x in prange(width, schedule='guided', nogil=True):
            ld_x = x
            pre_z_r = x_start + ld_x * pixel_size
            for y in range(height):
                ld_y = y
                z_r = pre_z_r
                z_i = y_start + ld_y * pixel_size
                content[x, y] = iterate(z_r, z_i, c_r, c_i, iterations)
        self.content = content

cdef class Mandelbrot(Fractale):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cython.boundscheck(False)  # turn off bounds-checking
    @cython.wraparound(False)  # turn off negative index wrapping
    cdef np.ndarray[DTYPE_t, ndim=2] _compute(self):
        """Compute fractal."""
        cdef:
            double c_r, c_i, z_r, z_i, tmp, x_start, y_start, ld_y, ld_x
            double real = self.real
            double imaginary = self.imaginary
            double pixel_size = self.pixel_size
            short y, x
            unsigned int i, iterations = self.iterations
            short width = self.width, height = self.height
            np.ndarray[DTYPE_t, ndim=2] content = np.zeros((width, height),
                                                           dtype=DTYPE)
        x_start = real - width / 2 * pixel_size
        y_start = imaginary - height / 2 * pixel_size
        for x in prange(width, schedule='guided', nogil=True):
            ld_x = x
            c_r = x_start + ld_x * pixel_size
            for y in range(height):
                ld_y = y
                c_i = y_start + ld_y * pixel_size
                content[x, y] = iterate(0, 0, c_r, c_i, iterations)
        self.content = content
