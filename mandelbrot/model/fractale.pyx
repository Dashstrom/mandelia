# distutils: language=c++

import numpy as np
import base64
from PIL import Image
from time import time

cimport numpy as np
cimport cython
from libc.string cimport memcpy
from cython.parallel import prange

DTYPE = np.uint32
ctypedef np.uint32_t DTYPE_t

COLORTYPE = np.uint8
ctypedef np.uint8_t COLORTYPE_t

CHAR_SIZE = sizeof(unsigned char)

DEF SAVE_SIZE = 35
DEF PIXEL_DEFAULT = 0.02
DEF MIN_PIXEL_SIZE = PIXEL_DEFAULT * 4

@cython.boundscheck(False)  # turn off bounds-checking
@cython.wraparound(False)  # turn off negative index wrapping
cdef np_mandelbrot(short width, short height, double pixel, double real,
                   double imaginary, unsigned int iteration_max):
    cdef:
        double c_r, c_i, z_r, z_i, tmp, x_start, y_start, ld_y, ld_x
        short y, x
        unsigned int i
        np.ndarray[DTYPE_t, ndim=2] content = np.zeros((width, height),
                                                       dtype=DTYPE)

    x_start = real - width / 2 * pixel
    y_start = imaginary - height / 2 * pixel
    for x in prange(width, schedule='guided', nogil=True):
        ld_x = x
        c_r = x_start + ld_x * pixel
        for y in range(height):
            ld_y = y
            c_i = y_start + ld_y * pixel
            z_r = 0
            z_i = 0
            for i in range(iteration_max):
                tmp = z_r
                z_r = z_r * z_r - z_i * z_i + c_r
                z_i = 2 * z_i * tmp + c_i
                if z_r * z_r + z_i * z_i > 4:
                    break
            content[x, y] = i + 1
    return content

@cython.boundscheck(False)  # turn off bounds-checking
@cython.wraparound(False)  # turn off negative index wrapping
cdef np_julia(short width, short height, double pixel, double c_r,
              double c_i, double real, double imaginary,
              unsigned int iteration_max):
    cdef:
        double z_r, z_i, pre_z_r, tmp, x_start, y_start, ld_y, ld_x
        short y, x
        unsigned int i
        np.ndarray[DTYPE_t, ndim=2] content = np.zeros((width, height),
                                                       dtype=DTYPE)

    x_start = real - width / 2 * pixel
    y_start = imaginary - height / 2 * pixel
    for x in prange(width, schedule='guided', nogil=True):
        ld_x = x
        pre_z_r = x_start + ld_x * pixel
        for y in range(height):
            ld_y = y
            z_r = pre_z_r
            z_i = y_start + ld_y * pixel
            for i in range(iteration_max):
                tmp = z_r
                z_r = z_r * z_r - z_i * z_i + c_r
                z_i = 2 * z_i * tmp + c_i
                if z_r * z_r + z_i * z_i > 10:
                    break
            content[x, y] = i + 1
    return content


@cython.boundscheck(False)  # turn off bounds-checking
@cython.wraparound(False)  # turn off negative index wrapping
cdef np_modulo_256_color(np.ndarray[DTYPE_t, ndim=2] content,
                         unsigned int iteration_max, unsigned char r,
                         unsigned char g, unsigned char b):
    cdef:
        short width, height, x, y
        unsigned int i
        np.ndarray[COLORTYPE_t, ndim=3] image

    width = content.shape[0]
    height = content.shape[1]
    image = np.zeros((height, width, 3), dtype=COLORTYPE)
    for x in prange(width, schedule='guided', nogil=True):
        for y in range(height):
            i = content[x, y]
            if i < iteration_max:
                image[y, x, 0] = r * i
                image[y, x, 1] = g * i
                image[y, x, 2] = b * i
    return image

cdef class Fractale:
    cdef:
        unsigned char r, g, b
        double real, imaginary, pixel
        double duration
        short width, height
        unsigned int iteration_max
        content, need_update

    def __init__(self, real=0, imaginary=0, pixel=PIXEL_DEFAULT,
                 iterations=2000, r=3, g=1, b=10, width=128, height=128):
        if width <= 0:
            raise ValueError("width must be positive")
        if height <= 0:
            raise ValueError("height must be positive")
        self.content = np.zeros((0, 0), dtype=DTYPE)
        self.real = real
        self.imaginary = imaginary
        self.pixel = pixel
        self.iteration_max = iterations
        self.width = width
        self.height = height
        self.duration = 0
        self.r = r
        self.g = g
        self.b = b
        self.need_update = True

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (f"<{self.__class__.__name__} {self.width}x{self.height} "
                f"zoom={self.get_zoom()} {self.real}{self.imaginary:+}i>")

    cpdef get_real(self):
        return self.real

    cpdef set_real(self, double real):
        self.real = real
        self.need_update = True

    cpdef get_imaginary(self):
        return self.imaginary

    cpdef set_imaginary(self, double imaginary):
        self.imaginary = imaginary
        self.need_update = True

    cpdef get_zoom(self):
        return int(1 / self.pixel) if self.pixel != 0 else 10 ** 30

    cpdef get_iteration_max(self):
        return self.iteration_max

    cpdef get_red(self):
        return self.r

    cpdef get_green(self):
        return self.g

    cpdef get_blue(self):
        return self.b

    cpdef rgb(self):
        return self.r, self.g, self.b

    cpdef set_color(self, unsigned char r, unsigned char g, unsigned char b):
        self.r = r
        self.b = b
        self.g = g

    cpdef set_iteration_max(self, unsigned int iteration_max):
        self.iteration_max = iteration_max
        self.need_update = True

    cpdef iterations_sum(self):
        return np.sum(self.content)

    cpdef iterations_per_pixel(self):
        cdef unsigned int pixels = self.width * self.height
        if pixels != 0:
            return self.iterations_sum() / pixels
        else:
            return 0

    cpdef iterations_per_second(self):
        if self.duration != 0:
            return self.iterations_sum() / self.duration
        else:
            return 0

    cdef check_min_size(self):
        cdef double multiplier = self.pixel / MIN_PIXEL_SIZE
        if self.pixel > MIN_PIXEL_SIZE:
            self.pixel = MIN_PIXEL_SIZE
            self.real = self.real / multiplier
            self.imaginary = self.imaginary / multiplier
            if -0.001 < self.real < 0.001:
                self.real = 0
            if -0.001 < self.imaginary < 0.001:
                self.imaginary = 0

    cpdef image(self):
        if self.need_update:
            self.compute()
        colored = np_modulo_256_color(
            self.content,
            self.iteration_max,
            self.r,
            self.g,
            self.b
        )
        return Image.fromarray(colored, 'RGB')

    cpdef resize(self, short width, short height):
        cdef double multiplier
        multiplier = width / self.width
        self.width = width
        self.height = height
        self.middle_zoom(multiplier)
        self.need_update = True

    cpdef screenshot(self, short width, short height):
        cdef:
            content_copy
            short x
            short w_copy = self.width
            short h_copy = self.height
            double real_copy = self.real
            double imaginary_copy = self.imaginary
            double pixel_copy = self.pixel
        if self.width != width or self.height != height:
            content_copy = self.content.copy()
            self.resize(width, height)
            img = self.image()
            self.real = real_copy
            self.imaginary = imaginary_copy
            self.pixel = pixel_copy
            self.content = content_copy
            self.width = w_copy
            self.height = h_copy
        img = self.image()
        return img

    cpdef top(self):
        self.pixel = PIXEL_DEFAULT
        self.need_update = True

    cpdef middle_zoom(self, double multiplier):
        self.zoom(self.width // 2, self.height // 2, multiplier)

    cpdef zoom(self, short x, short y, double multiplier):
        cdef double pixel = self.pixel, real = self.real, imaginary = self.imaginary
        self.real = (real * 1 / multiplier
                     + (real + x * pixel - self.width / 2 * pixel)
                     * (1 - 1 / multiplier))
        self.imaginary = (imaginary * 1 / multiplier
                          + (imaginary + y * pixel - self.height / 2 * pixel)
                          * (1 - 1 / multiplier))
        self.pixel /= multiplier
        self.check_min_size()
        self.need_update = True

    cpdef reset(self):
        self.real = 0
        self.imaginary = 0
        self.pixel = PIXEL_DEFAULT
        self.need_update = True

    cdef compute(self):
        raise NotImplementedError()

    cpdef code(self):
        """Return str in base 64 representative of the fractale."""
        return str(base64.b64encode(self.data()))[2:-1]

    cpdef from_code(self, code):
        """Load data encoded in base 64 on the fractale."""
        self.from_data(base64.b64decode(code))

    cpdef data(self):
        """Return bytes representative of the fractale."""
        cdef:
            unsigned char arr[SAVE_SIZE]
        arr[:] = [0] * SAVE_SIZE
        memcpy(arr, &self.real, 8 * CHAR_SIZE)
        memcpy(arr + 8, &self.imaginary, 8 * CHAR_SIZE)
        memcpy(arr + 16, &self.pixel, 8 * CHAR_SIZE)
        memcpy(arr + 24, &self.iteration_max, 4 * CHAR_SIZE)
        memcpy(arr + 28, &self.r, CHAR_SIZE)
        memcpy(arr + 29, &self.g, CHAR_SIZE)
        memcpy(arr + 30, &self.b, CHAR_SIZE)
        memcpy(arr + 31, &self.width, 2 * CHAR_SIZE)
        memcpy(arr + 33, &self.height, 2 * CHAR_SIZE)
        return bytearray([arr[i] for i in range(SAVE_SIZE)])

    cpdef from_data(self, bytes_):
        """Load data on the fractale."""
        cdef:
            unsigned char arr[SAVE_SIZE]
            short width = self.width, height = self.height
        if not isinstance(bytes_, (bytes, bytearray)):
            raise TypeError(
                f"Invalid type, attempt bytes but receive {type(bytes_)}")
        elif len(bytes_) != SAVE_SIZE:
            raise ValueError(f"bytes must contain {SAVE_SIZE} byte")
        arr[:] = bytes_
        memcpy(&self.real, arr, 8 * CHAR_SIZE)
        memcpy(&self.imaginary, arr + 8, 8 * CHAR_SIZE)
        memcpy(&self.pixel, arr + 16, 8 * CHAR_SIZE)
        memcpy(&self.iteration_max, arr + 24, 4 * CHAR_SIZE)
        memcpy(&self.r, arr + 28, CHAR_SIZE)
        memcpy(&self.g, arr + 29, CHAR_SIZE)
        memcpy(&self.b, arr + 30, CHAR_SIZE)
        memcpy(&self.width, arr + 31, 2 * CHAR_SIZE)
        memcpy(&self.height, arr + 33, 2 * CHAR_SIZE)
        self.resize(width, height)

    cpdef get_width(self):
        return self.width

    cpdef get_height(self):
        return self.height

    cpdef real_at_x(self, short x):
        cdef double start_r = self.real - (self.width * self.pixel) / 2
        return (self.real - (self.width * self.pixel) / 2) + x * self.pixel

    cpdef imaginary_at_y(self, short y):
        cdef double start_i = self.imaginary - (self.height * self.pixel) / 2
        return start_i + y * self.pixel

cdef class Julia(Fractale):
    cdef:
        double c_r, c_i
    def __init__(self, *args, **kwargs):
        self.c_r = 0
        self.c_i = 0
        self.imaginary = 0
        self.real = 0
        super().__init__(*args, **kwargs)

    cpdef get_real(self) :
        return self.real

    cpdef get_imaginary(self):
        return self.imaginary

    cpdef set_real(self, double c_r):
        self.c_r = c_r
        self.need_update = True

    cpdef set_imaginary(self, double c_i):
        self.c_i = c_i
        self.need_update = True

    cdef compute(self):
        cdef:
            double start = time()
        self.content = np_julia(self.width, self.height, self.pixel,
                                self.c_r, self.c_i, self.real,
                                self.imaginary, self.iteration_max)
        self.duration = time() - start

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (f"<{self.__class__.__name__} {self.width}x{self.height} "
                f"zoom={self.get_zoom()} {self.real}{self.imaginary:+}i "
                f"c={self.c_r}{self.c_i:+}i>")

    cpdef data(self):
        """Return bytes representative of the fractale."""
        cdef:
            unsigned char arr[16]
            bytearray data
        arr[:] = [0] * 16
        memcpy(arr, &self.c_r, 8 * CHAR_SIZE)
        memcpy(arr + 8, &self.c_i, 8 * CHAR_SIZE)
        data = super().data()
        data.extend(arr)
        return data

    cpdef from_data(self, bytes_):
        """Load data on the fractale."""
        cdef:
            unsigned char arr[16]
        if not isinstance(bytes_, (bytes, bytearray)):
            raise TypeError(
                f"Invalid type, attempt bytes but receive {type(bytes_)}")
        elif len(bytes_) != SAVE_SIZE:
            raise ValueError(f"bytes must contain {SAVE_SIZE} byte")
        arr[:] = bytes_[:16]
        memcpy(&self.c_r, arr, 8 * CHAR_SIZE)
        memcpy(&self.c_i, arr, 8 * CHAR_SIZE)
        super().from_data(bytes_[16:])


cdef class Mandelbrot(Fractale):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    cdef compute(self):
        cdef:
            double start = time()
        self.content = np_mandelbrot(self.width, self.height, self.pixel,
                                     self.real, self.imaginary,
                                     self.iteration_max)
        self.duration = time() - start
        print(f"{self.duration * 1000:.2f}ms")
