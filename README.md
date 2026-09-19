# Sierpinski Triangle Fractal Generator (CGM Lab Project)
### B.Tech CSE (AI) | Computer Graphics & Multimedia Laboratory

A high-performance C++ implementation of the Sierpinski Triangle fractal using **SFML** and **Dear ImGui (ImGui-SFML)**. The application features real-time visualization of both the **Chaos Game (Random Midpoint Iteration)** and **Recursive Geometric Subdivision**, complete with interactive GUI controls, dynamic color themes, and a pure SFML fallback.

---

## 🌟 Key Features

1. **User Input for Number of Polygon Sides (N >= 3):**
   - **Triangle (N=3):** Classic Sierpinski Gasket ($r = 0.5$).
   - **Square (N=4):** Sierpinski Carpet with IFS non-adjacent restriction rule ($r = 0.5$).
   - **Pentagon (N=5):** Dürer's Pentagasket with Golden Ratio contraction ($r = \frac{3-\sqrt{5}}{2} \approx 0.382$).
   - **Hexagon (N=6):** Hexaflake ($r = 1/3 \approx 0.333$).
   - **Octagon (N=8):** Octaflake ($r = \frac{1}{2+\sqrt{2}} \approx 0.293$).
   - **Arbitrary N-Gons up to N=12:** Optimal mathematical jump ratios computed automatically!

2. **Chaos Game (Random Contraction Method):**
   - Real-time point-by-point generation with adjustable speed (10 to 10,000 points/frame).
   - Dynamic point limits up to 500,000 points with smooth 60 FPS performance via `sf::RenderTexture` hardware caching.
   - Interactive point size scaling (1.0 to 6.0 px).
   - Animated wandering tracker showing the currently evaluated point.

2. **Recursive Subdivision Method:**
   - Interactive recursion depth slider (depth 0 to 8, rendering up to 6,561 sub-triangles).
   - Toggle between **Solid Filled** triangles and **Wireframe Perimeter** modes.

3. **Color Schemes:**
   - **IFS Vertex-Based:** Colors points based on which attractor vertex was chosen (visual proof of Iterated Function System affine maps).
   - **Solid Custom:** Interactive RGB color picker.
   - **Height Gradient:** Smooth vertical gradient along the Y-axis.
   - **Rainbow Hue:** Dynamic chromatic progression.

4. **Dual Interface Architecture:**
   - **ImGui-SFML GUI:** Sliders, buttons, checkboxes, color pickers, and real-time FPS/progress metrics.
   - **Pure SFML Keyboard Fallback:** Fully operational HUD and keyboard shortcuts if ImGui is not installed.

---

## 📁 Project Structure

```
CGM PROJECT/
├── main.cpp              # Unified source file (supports both ImGui-SFML and Pure SFML)
├── main_pure_sfml.cpp    # Pure SFML entry point (zero ImGui dependencies)
├── CMakeLists.txt        # Modern CMake configuration with FetchContent
├── Makefile              # Linux / MinGW build script
├── build_pure.bat        # 1-Click Windows batch script for MinGW
├── README.md             # Compilation and setup instructions
└── THEORY_AND_VIVA.md    # Math theory, Hausdorff dimension proof & viva Q&A
```

---

## 🚀 Build & Compilation Instructions

### Option 1: Standalone Pure SFML (Recommended for Lab Exams)
Requires **only SFML 2.5+** installed on the computer. No extra dependencies needed.

#### On Windows (MinGW g++):
```bash
g++ -std=c++17 -O3 -DUSE_IMGUI=0 main_pure_sfml.cpp -lsfml-graphics -lsfml-window -lsfml-system -o sierpinski.exe
.\sierpinski.exe
```
*(Or simply double-click `build_pure.bat`)*

#### On Linux (Ubuntu / Debian):
```bash
# 1. Install SFML
sudo apt update && sudo apt install libsfml-dev

# 2. Compile and run
g++ -std=c++17 -O3 -DUSE_IMGUI=0 main_pure_sfml.cpp -lsfml-graphics -lsfml-window -lsfml-system -o sierpinski
./sierpinski
```

---

### Option 2: Full Build with ImGui-SFML GUI

#### Method A: Using CMake (Automated)
CMake will automatically download and link Dear ImGui and ImGui-SFML via `FetchContent`:
```bash
mkdir build && cd build
cmake ..
cmake --build . --config Release
./SierpinskiFractal
```

#### Method B: Manual Linking with MinGW / GCC
1. Download Dear ImGui (v1.89+): [github.com/ocornut/imgui](https://github.com/ocornut/imgui)
2. Download ImGui-SFML: [github.com/SFML/imgui-sfml](https://github.com/SFML/imgui-sfml)
3. Place `imgui/` and `imgui-sfml/` in the project directory.
4. Compile with:
```bash
g++ -std=c++17 -O3 -DUSE_IMGUI=1 \
    -I./imgui -I./imgui-sfml \
    main.cpp \
    ./imgui/imgui.cpp ./imgui/imgui_draw.cpp ./imgui/imgui_widgets.cpp ./imgui/imgui_tables.cpp \
    ./imgui-sfml/imgui-SFML.cpp \
    -lsfml-graphics -lsfml-window -lsfml-system -lopengl32 \
    -o sierpinski_gui.exe
```

---

## 🎮 Keyboard Controls & Shortcuts

| Key | Action | Description |
| :---: | :--- | :--- |
| **`[M]`** | **Switch Mode** | Toggles between Chaos Game and Recursive Subdivision |
| **`[Space]`** | **Pause / Resume** | Pauses or resumes point generation in Chaos Game |
| **`[R]`** | **Reset** | Clears points or resets recursive mesh |
| **`[C]`** | **Cycle Colors** | Switches between Custom, Vertex IFS, Height Gradient, Rainbow |
| **`[Up]`** | **Speed / Depth +** | Increases points/frame (Chaos) or increases recursion depth |
| **`[Down]`**| **Speed / Depth -** | Decreases points/frame (Chaos) or decreases recursion depth |
| **`[+]` / `[-]`** | **Point Size** | Increases or decreases point/pixel diameter |
| **`[W]`** | **Wireframe** | Toggles wireframe outline vs solid fill in Recursive mode |

---

## 🔬 Mathematical Summary for Viva

- **Self-Similarity:** The triangle consists of $N = 3$ identical self-similar copies, each scaled by a factor of $s = 1/2$.
- **Hausdorff Dimension:**
  $$D = \frac{\log(N)}{\log(1/s)} = \frac{\log 3}{\log 2} \approx 1.58496$$
- **Iterated Function System (IFS):**
  $$f_i(P) = \frac{1}{2}P + \frac{1}{2}V_i, \quad i \in \{0, 1, 2\}$$
  By Hutchinson's Theorem and Banach's Fixed-Point Theorem, the Sierpinski gasket is the unique compact attractor invariant under $A = \bigcup_{i=0}^2 f_i(A)$.
- *See [THEORY_AND_VIVA.md](THEORY_AND_VIVA.md) for full derivations, paradoxes, and viva questions.*
