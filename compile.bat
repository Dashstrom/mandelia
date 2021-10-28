py setup.py build_ext --inplace
if "%ERRORLEVEL%" NEQ "0" (exit /B)

RMDIR /s /q "mandelbrot/model/mandelbrot"
RMDIR /s /q "build"
py -m mandelbrot
: pyinstaller --add-data "logo.ico";"." --noconsole --onefile --name=Mandelbrot --icon=logo.ico main.py