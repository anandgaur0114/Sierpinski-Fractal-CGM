cmake_minimum_required(VERSION 3.16)
project(SierpinskiFractalCGM VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

option(ENABLE_IMGUI "Enable ImGui-SFML GUI interface" ON)

# Find SFML (Graphics, Window, System)
find_package(SFML 2.5 COMPONENTS graphics window system REQUIRED)

if(ENABLE_IMGUI)
    include(FetchContent)

    # Fetch Dear ImGui
    FetchContent_Declare(
        imgui
        GIT_REPOSITORY https://github.com/ocornut/imgui.git
        GIT_TAG        v1.89.9
    )
    FetchContent_MakeAvailable(imgui)

    # Fetch ImGui-SFML
    FetchContent_Declare(
        imgui-sfml
        GIT_REPOSITORY https://github.com/SFML/imgui-sfml.git
        GIT_TAG        v2.6
    )
    set(IMGUI_DIR ${imgui_SOURCE_DIR} CACHE PATH "ImGui source dir")
    set(IMGUI_SFML_FIND_SFML OFF CACHE BOOL "Don't search for SFML inside ImGui-SFML")
    FetchContent_MakeAvailable(imgui-sfml)

    add_executable(SierpinskiFractal main.cpp)
    target_compile_definitions(SierpinskiFractal PRIVATE USE_IMGUI=1)
    target_link_libraries(SierpinskiFractal PRIVATE sfml-graphics sfml-window sfml-system ImGui-SFML::ImGui-SFML)
else()
    add_executable(SierpinskiFractal main.cpp)
    target_compile_definitions(SierpinskiFractal PRIVATE USE_IMGUI=0)
    target_link_libraries(SierpinskiFractal PRIVATE sfml-graphics sfml-window sfml-system)
endif()

# Standalone Pure SFML target
add_executable(SierpinskiPure main_pure_sfml.cpp)
target_link_libraries(SierpinskiPure PRIVATE sfml-graphics sfml-window sfml-system)
