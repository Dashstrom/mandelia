py setup.py build_ext --inplace
MOVE /Y "fractale.cp39-win_amd64.pyd" "mandelbrot\model"
DEL "mandelbrot\model\fractale.cpp"
RMDIR "build" /s /q
: pyinstaller --add-data "logo.ico";"." --noconsole --onefile --name=Mandelbrot --icon=logo.ico main.py