@echo off
echo ==============================================================================
echo Compiling Pure SFML Sierpinski Fractal Generator...
echo ==============================================================================

if exist "SFML-2.5.1\include" (
    g++ -std=c++14 -O3 -I"SFML-2.5.1\include" -L"SFML-2.5.1\lib" -DUSE_IMGUI=0 main_pure_sfml.cpp -lsfml-graphics -lsfml-window -lsfml-system -o sierpinski_pure.exe
) else (
    g++ -std=c++14 -O3 -DUSE_IMGUI=0 main_pure_sfml.cpp -lsfml-graphics -lsfml-window -lsfml-system -o sierpinski_pure.exe
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Compiled successfully! Output: sierpinski_pure.exe
    echo.
    echo Starting Sierpinski Fractal Generator...
    start "" sierpinski_pure.exe
) else (
    echo.
    echo [ERROR] Compilation failed. Ensure g++ (MinGW) is in your system PATH.
    pause
)
