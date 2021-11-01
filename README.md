# Mandelbrot

Application to visualize the fractal of mandelbrot and julia.

```
yay -S tk
py setup.py build_ext --inplace

rm -rf "mandelbrot/model/mandelbrot"
rm rf "build"
py -m mandelbrot
```