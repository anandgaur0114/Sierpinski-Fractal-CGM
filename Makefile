# ==============================================================================
# Makefile for Sierpinski Triangle Fractal Generator (CGM Lab Project)
# ==============================================================================

CXX = g++
CXXFLAGS = -std=c++17 -O3 -Wall -Wextra

# SFML Flags
SFML_LIBS = -lsfml-graphics -lsfml-window -lsfml-system

# ImGui Source Files (if linking manually in project directory)
IMGUI_DIR = ./imgui
IMGUI_SFML_DIR = ./imgui-sfml
IMGUI_SOURCES = $(wildcard $(IMGUI_DIR)/*.cpp) $(IMGUI_SFML_DIR)/imgui-SFML.cpp
IMGUI_INCLUDES = -I$(IMGUI_DIR) -I$(IMGUI_SFML_DIR)

all: pure

# Target 1: Pure SFML (No external ImGui dependencies, always compiles in lab)
pure: main_pure_sfml.cpp
	$(CXX) $(CXXFLAGS) -DUSE_IMGUI=0 main_pure_sfml.cpp -o sierpinski_pure $(SFML_LIBS)
	@echo "Build successful! Run ./sierpinski_pure"

# Target 2: With ImGui-SFML (requires imgui and imgui-sfml sources)
imgui: main.cpp $(IMGUI_SOURCES)
	$(CXX) $(CXXFLAGS) -DUSE_IMGUI=1 $(IMGUI_INCLUDES) main.cpp $(IMGUI_SOURCES) -o sierpinski_gui $(SFML_LIBS) -lGL
	@echo "Build with ImGui successful! Run ./sierpinski_gui"

clean:
	rm -f sierpinski_pure sierpinski_pure.exe sierpinski_gui sierpinski_gui.exe *.o
