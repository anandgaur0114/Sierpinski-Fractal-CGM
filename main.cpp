/**
 * ============================================================================
 * Project: Generalized N-Gon Fractal Generator (Chaos Game & N-Flakes)
 * Course : Computer Graphics & Multimedia (CGM) Lab - B.Tech CSE (AI)
 * 
 * Major Features:
 *   1. USER INPUT FOR NUMBER OF SIDES (N >= 3):
 *      - Triangle (N=3): Classic Sierpinski Gasket (Jump ratio r = 1/2)
 *      - Square (N=4): Sierpinski Carpet (with IFS restriction rule)
 *      - Pentagon (N=5): Dürer's Pentagasket / Golden Ratio (r ~ 0.382)
 *      - Hexagon (N=6): Hexaflake (r = 1/3)
 *      - Octagon (N=8): Octaflake (r ~ 0.293)
 *      - Arbitrary N-gons up to N=12 with mathematically computed optimal ratios!
 *   2. MULTIPLE USER INPUT MODES:
 *      - Console prompt at startup (`cin >> numSides >> ...`)
 *      - Clickable on-screen GUI buttons for [Sides - / +] and [Ratio - / +]
 *      - Interactive Mouse: click & drag any of the N vertices in real time!
 *      - Click-to-seed: click anywhere to set custom starting point
 *      - Full keyboard shortcuts: [N] increase sides, [Shift+N] decrease sides
 * ============================================================================
 */

#ifndef USE_IMGUI
#define USE_IMGUI 0
#endif

#include <SFML/Graphics.hpp>
#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <sstream>
#include <iomanip>
#include <string>
#include <algorithm>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// ============================================================================
// Data Structures & Enums
// ============================================================================

enum class GenerationMode {
    ChaosGame = 0,
    RecursiveSubdivision = 1
};

enum class ColorScheme {
    VertexBased = 0,       // Unique color per vertex (IFS decomposition)
    CyanSolid = 1,         // Electric Cyan
    LimeSolid = 2,         // Neon Lime
    AmberSolid = 3,        // Sunset Gold / Amber
    HeightGradient = 4,    // Linear gradient along Y-axis
    Rainbow = 5            // Dynamic hue progression
};

struct GUIButton {
    sf::FloatRect bounds;
    std::string label;
    int id;
};

// ============================================================================
// Configuration & Simulation State
// ============================================================================

struct FractalConfig {
    unsigned int windowWidth = 1180;
    unsigned int windowHeight = 850;
    float controlPanelWidth = 330.0f; // Reserved sidebar width

    // General N-Gon parameters
    int numSides = 3;                // N-gon side count (3 to 12)
    const int minSides = 3;
    const int maxSides = 12;
    float jumpRatio = 0.5f;          // r in P_new = r * P + (1 - r) * V
    bool autoJumpRatio = true;       // Automatically compute optimal ratio for N
    bool noRepeatRule = false;       // Restriction: cannot pick same vertex consecutively

    GenerationMode mode = GenerationMode::ChaosGame;
    ColorScheme colorScheme = ColorScheme::VertexBased;

    // Simulation parameters
    size_t targetPoints = 100000;
    size_t pointsPerFrame = 1200;
    float pointSize = 1.5f;
    bool isPaused = false;

    // Recursive Subdivision parameters (for N=3)
    int recursionDepth = 5;
    const int maxRecursionDepth = 8;
    bool wireframeMode = false;
} config;

// Polygon vertices defining the attractor
std::vector<sf::Vector2f> polygonVertices;
std::vector<sf::Color> vertexPalette;
int draggedVertex = -1;
int hoveredVertex = -1;

// Chaos Game State
sf::Vector2f currentChaosPoint;
size_t currentPointCount = 0;
int lastChosenVertex = -1;

// Persistent SFML Buffers
sf::RenderTexture chaosCanvas;
sf::VertexArray recursiveTriangles(sf::Triangles);
sf::VertexArray recursiveLines(sf::Lines);

// Random Number Generation
std::random_device rd;
std::mt19937 rng(rd());
std::uniform_real_distribution<float> unitDist(0.0f, 1.0f);

// Font for HUD
sf::Font hudFont;
bool fontLoaded = false;

// List of interactive buttons
std::vector<GUIButton> guiButtons;

// ============================================================================
// Mathematical Helper Functions
// ============================================================================

/**
 * Computes the optimal jump contraction factor r for an arbitrary regular N-gon
 * so that adjacent self-similar copies touch at their perimeter.
 * 
 * Formula:
 *   r = 1 / ( 2 * ( 1 + sum_{k=1}^{floor(N/4)} cos(2*pi*k / N) ) )
 */
float computeOptimalJumpRatio(int n) {
    if (n <= 3) return 0.5f;
    if (n == 4) return 0.5f; // With no-repeat rule, 0.5 yields the Sierpinski Carpet
    float sumCos = 0.0f;
    int limit = n / 4;
    for (int k = 1; k <= limit; ++k) {
        sumCos += std::cos(2.0f * static_cast<float>(M_PI) * static_cast<float>(k) / static_cast<float>(n));
    }
    return 1.0f / (2.0f * (1.0f + sumCos));
}

/**
 * Generates N distinct visually pleasing colors around the HSV color wheel.
 */
void generateColorPalette(int n) {
    vertexPalette.clear();
    for (int i = 0; i < n; ++i) {
        float hue = static_cast<float>(i) / static_cast<float>(n) * 6.0f;
        int sector = static_cast<int>(hue);
        float f = hue - sector;
        float q = 1.0f - f;
        float r = 0, g = 0, b = 0;
        switch (sector % 6) {
            case 0: r = 1; g = f; b = 0; break;
            case 1: r = q; g = 1; b = 0; break;
            case 2: r = 0; g = 1; b = f; break;
            case 3: r = 0; g = q; b = 1; break;
            case 4: r = f; g = 0; b = 1; break;
            case 5: r = 1; g = 0; b = q; break;
        }
        vertexPalette.push_back(sf::Color(
            static_cast<sf::Uint8>(r * 255),
            static_cast<sf::Uint8>(g * 255),
            static_cast<sf::Uint8>(b * 255)
        ));
    }
}

// ============================================================================
// Function Declarations
// ============================================================================

void initPolygon(int n, sf::Vector2u windowSize);
void resetChaosGame(bool keepSeed = false);
void chaosGameStep(size_t count);
void generateRecursive(int depth, sf::Vector2f p1, sf::Vector2f p2, sf::Vector2f p3);
void rebuildRecursiveMesh();
sf::Color evaluateColor(sf::Vector2f pos, int chosenVertexIndex, size_t pointIndex);
void setupButtons();
void handleButtonClick(int buttonId, sf::RenderWindow& window);
void promptConsoleInput(sf::RenderWindow& window);
void renderHUD(sf::RenderWindow& window, float fps, sf::Vector2i mousePos);

// ============================================================================
// 1. initPolygon: Regular Polygon Calculation
// ============================================================================

void initPolygon(int n, sf::Vector2u windowSize) {
    config.numSides = std::max(config.minSides, std::min(config.maxSides, n));
    if (config.autoJumpRatio) {
        config.jumpRatio = computeOptimalJumpRatio(config.numSides);
    }
    // Automatically enable no-repeat rule for Square (N=4) to produce Sierpinski Carpet
    if (config.numSides == 4) {
        config.noRepeatRule = true;
    }

    generateColorPalette(config.numSides);

    float renderAreaWidth = static_cast<float>(windowSize.x) - config.controlPanelWidth;
    float renderAreaHeight = static_cast<float>(windowSize.y);
    float centerX = config.controlPanelWidth + (renderAreaWidth / 2.0f);
    float centerY = renderAreaHeight / 2.0f;

    float padding = 55.0f;
    float radius = std::min(renderAreaWidth / 2.0f, renderAreaHeight / 2.0f) - padding;

    polygonVertices.resize(config.numSides);
    for (int i = 0; i < config.numSides; ++i) {
        // Offset angle so polygon points upright
        float angle = -static_cast<float>(M_PI) / 2.0f + (2.0f * static_cast<float>(M_PI) * i / config.numSides);
        polygonVertices[i] = sf::Vector2f(
            centerX + radius * std::cos(angle),
            centerY + radius * std::sin(angle)
        );
    }

    if (chaosCanvas.getSize().x != windowSize.x || chaosCanvas.getSize().y != windowSize.y) {
        chaosCanvas.create(windowSize.x, windowSize.y);
        chaosCanvas.setSmooth(true);
    }
    chaosCanvas.clear(sf::Color(18, 18, 24));
    chaosCanvas.display();
}

// ============================================================================
// 2. resetChaosGame: Seed & Warmup
// ============================================================================

void resetChaosGame(bool keepSeed) {
    chaosCanvas.clear(sf::Color(18, 18, 24));
    chaosCanvas.display();
    currentPointCount = 0;
    lastChosenVertex = -1;

    if (!keepSeed && !polygonVertices.empty()) {
        float minX = polygonVertices[0].x, maxX = polygonVertices[0].x;
        float minY = polygonVertices[0].y, maxY = polygonVertices[0].y;
        for (const auto& v : polygonVertices) {
            minX = std::min(minX, v.x);
            maxX = std::max(maxX, v.x);
            minY = std::min(minY, v.y);
            maxY = std::max(maxY, v.y);
        }
        currentChaosPoint = sf::Vector2f(
            minX + unitDist(rng) * (maxX - minX),
            minY + unitDist(rng) * (maxY - minY)
        );
    }

    // Warmup iterations to attract point onto the fractal boundary
    std::uniform_int_distribution<int> vDist(0, config.numSides - 1);
    for (int i = 0; i < 30; ++i) {
        int vIdx = vDist(rng);
        if (config.noRepeatRule && vIdx == lastChosenVertex) {
            vIdx = (vIdx + 1) % config.numSides;
        }
        lastChosenVertex = vIdx;
        currentChaosPoint = (1.0f - config.jumpRatio) * currentChaosPoint + config.jumpRatio * polygonVertices[vIdx];
    }
}

// ============================================================================
// 3. evaluateColor: Shading Logic
// ============================================================================

sf::Color evaluateColor(sf::Vector2f pos, int chosenVertexIndex, size_t pointIndex) {
    switch (config.colorScheme) {
        case ColorScheme::VertexBased: {
            if (chosenVertexIndex >= 0 && chosenVertexIndex < static_cast<int>(vertexPalette.size())) {
                return vertexPalette[chosenVertexIndex];
            }
            return sf::Color(0, 220, 255);
        }
        case ColorScheme::CyanSolid:
            return sf::Color(0, 220, 255);
        case ColorScheme::LimeSolid:
            return sf::Color(110, 255, 70);
        case ColorScheme::AmberSolid:
            return sf::Color(255, 185, 35);
        case ColorScheme::HeightGradient: {
            if (polygonVertices.empty()) return sf::Color::Cyan;
            float minY = polygonVertices[0].y, maxY = polygonVertices[0].y;
            for (const auto& v : polygonVertices) {
                minY = std::min(minY, v.y);
                maxY = std::max(maxY, v.y);
            }
            float t = (maxY > minY) ? (pos.y - minY) / (maxY - minY) : 0.5f;
            t = std::max(0.0f, std::min(1.0f, t));
            sf::Uint8 r = static_cast<sf::Uint8>((1.0f - t) * 255 + t * 138);
            sf::Uint8 g = static_cast<sf::Uint8>((1.0f - t) * 215 + t * 43);
            sf::Uint8 b = static_cast<sf::Uint8>((1.0f - t) * 30  + t * 226);
            return sf::Color(r, g, b);
        }
        case ColorScheme::Rainbow: {
            float hue = std::fmod(static_cast<float>(pointIndex) * 0.0015f, 1.0f) * 6.0f;
            int i = static_cast<int>(hue);
            float f = hue - i;
            float q = 1.0f - f;
            float r = 0, g = 0, b = 0;
            switch (i % 6) {
                case 0: r = 1; g = f; b = 0; break;
                case 1: r = q; g = 1; b = 0; break;
                case 2: r = 0; g = 1; b = f; break;
                case 3: r = 0; g = q; b = 1; break;
                case 4: r = f; g = 0; b = 1; break;
                case 5: r = 1; g = 0; b = q; break;
            }
            return sf::Color(static_cast<sf::Uint8>(r * 255), static_cast<sf::Uint8>(g * 255), static_cast<sf::Uint8>(b * 255));
        }
    }
    return sf::Color::Cyan;
}

// ============================================================================
// 4. chaosGameStep: Generalized N-Gon Midpoint/Contraction Step
// ============================================================================

void chaosGameStep(size_t count) {
    if (currentPointCount >= config.targetPoints || polygonVertices.empty()) return;

    size_t actualPoints = std::min(count, config.targetPoints - currentPointCount);
    if (actualPoints == 0) return;

    std::uniform_int_distribution<int> vDist(0, config.numSides - 1);
    float r = config.jumpRatio;

    if (config.pointSize <= 1.0f) {
        sf::VertexArray pointBatch(sf::Points, actualPoints);
        for (size_t i = 0; i < actualPoints; ++i) {
            int chosenVertex = vDist(rng);
            if (config.noRepeatRule && chosenVertex == lastChosenVertex) {
                chosenVertex = (chosenVertex + 1 + (vDist(rng) % (config.numSides - 1))) % config.numSides;
            }
            lastChosenVertex = chosenVertex;

            // Jump: P_new = (1 - r) * P + r * V
            currentChaosPoint = (1.0f - r) * currentChaosPoint + r * polygonVertices[chosenVertex];

            pointBatch[i].position = currentChaosPoint;
            pointBatch[i].color = evaluateColor(currentChaosPoint, chosenVertex, currentPointCount + i);
        }
        chaosCanvas.draw(pointBatch);
    } else {
        sf::CircleShape stamp(config.pointSize * 0.5f);
        stamp.setOrigin(config.pointSize * 0.5f, config.pointSize * 0.5f);
        for (size_t i = 0; i < actualPoints; ++i) {
            int chosenVertex = vDist(rng);
            if (config.noRepeatRule && chosenVertex == lastChosenVertex) {
                chosenVertex = (chosenVertex + 1 + (vDist(rng) % (config.numSides - 1))) % config.numSides;
            }
            lastChosenVertex = chosenVertex;

            currentChaosPoint = (1.0f - r) * currentChaosPoint + r * polygonVertices[chosenVertex];

            stamp.setPosition(currentChaosPoint);
            stamp.setFillColor(evaluateColor(currentChaosPoint, chosenVertex, currentPointCount + i));
            chaosCanvas.draw(stamp);
        }
    }

    chaosCanvas.display();
    currentPointCount += actualPoints;
}

// ============================================================================
// 5. Recursive Subdivision (Sierpinski Splitting for N=3)
// ============================================================================

void generateRecursive(int depth, sf::Vector2f p1, sf::Vector2f p2, sf::Vector2f p3) {
    if (depth <= 0) {
        sf::Color c1 = evaluateColor(p1, 0, 0);
        sf::Color c2 = evaluateColor(p2, 1, 1);
        sf::Color c3 = evaluateColor(p3, 2, 2);

        if (!config.wireframeMode) {
            recursiveTriangles.append(sf::Vertex(p1, c1));
            recursiveTriangles.append(sf::Vertex(p2, c2));
            recursiveTriangles.append(sf::Vertex(p3, c3));
        } else {
            recursiveLines.append(sf::Vertex(p1, c1));
            recursiveLines.append(sf::Vertex(p2, c2));
            recursiveLines.append(sf::Vertex(p2, c2));
            recursiveLines.append(sf::Vertex(p3, c3));
            recursiveLines.append(sf::Vertex(p3, c3));
            recursiveLines.append(sf::Vertex(p1, c1));
        }
        return;
    }

    sf::Vector2f m12 = 0.5f * (p1 + p2);
    sf::Vector2f m23 = 0.5f * (p2 + p3);
    sf::Vector2f m31 = 0.5f * (p3 + p1);

    generateRecursive(depth - 1, p1, m12, m31);
    generateRecursive(depth - 1, m12, p2, m23);
    generateRecursive(depth - 1, m31, m23, p3);
}

void rebuildRecursiveMesh() {
    recursiveTriangles.clear();
    recursiveLines.clear();
    if (polygonVertices.size() >= 3) {
        generateRecursive(config.recursionDepth, polygonVertices[0], polygonVertices[1], polygonVertices[2]);
    }
}

// ============================================================================
// 6. Interactive GUI Setup
// ============================================================================

void setupButtons() {
    guiButtons.clear();
    float x = 20.0f;
    float w = 290.0f;

    // Row 1: N-Gon Sides Controls
    guiButtons.push_back({ sf::FloatRect(x, 145.0f, 140.0f, 30.0f), "Sides - (N)", 1 });
    guiButtons.push_back({ sf::FloatRect(x + 150.0f, 145.0f, 140.0f, 30.0f), "Sides + (N)", 2 });

    // Row 2: Jump Ratio Controls
    guiButtons.push_back({ sf::FloatRect(x, 180.0f, 140.0f, 30.0f), "Ratio -", 3 });
    guiButtons.push_back({ sf::FloatRect(x + 150.0f, 180.0f, 140.0f, 30.0f), "Ratio +", 4 });

    // Row 3: Mode Switch & Rule Toggle
    guiButtons.push_back({ sf::FloatRect(x, 215.0f, 140.0f, 30.0f), "Mode Switch", 5 });
    guiButtons.push_back({ sf::FloatRect(x + 150.0f, 215.0f, 140.0f, 30.0f), "Rule: Toggle", 6 });

    // Row 4: Pause & Reset
    guiButtons.push_back({ sf::FloatRect(x, 250.0f, 140.0f, 30.0f), "[Space] Pause", 7 });
    guiButtons.push_back({ sf::FloatRect(x + 150.0f, 250.0f, 140.0f, 30.0f), "[R] Reset", 8 });

    // Row 5: Speed Controls
    guiButtons.push_back({ sf::FloatRect(x, 285.0f, 140.0f, 30.0f), "Speed -", 9 });
    guiButtons.push_back({ sf::FloatRect(x + 150.0f, 285.0f, 140.0f, 30.0f), "Speed +", 10 });

    // Row 6: Point Size
    guiButtons.push_back({ sf::FloatRect(x, 320.0f, 140.0f, 30.0f), "Size -", 11 });
    guiButtons.push_back({ sf::FloatRect(x + 150.0f, 320.0f, 140.0f, 30.0f), "Size +", 12 });

    // Row 7: Color Scheme
    guiButtons.push_back({ sf::FloatRect(x, 355.0f, w, 30.0f), "Cycle Color Scheme", 13 });

    // Row 8: Console Input & Reset Shape
    guiButtons.push_back({ sf::FloatRect(x, 390.0f, w, 30.0f), "[I] Enter Parameters in Console", 14 });
    guiButtons.push_back({ sf::FloatRect(x, 425.0f, w, 30.0f), "Reset Regular Polygon Geometry", 15 });
}

void handleButtonClick(int buttonId, sf::RenderWindow& window) {
    switch (buttonId) {
        case 1: // Sides -
            if (config.numSides > config.minSides) {
                initPolygon(config.numSides - 1, window.getSize());
                resetChaosGame();
                if (config.mode == GenerationMode::RecursiveSubdivision) rebuildRecursiveMesh();
            }
            break;
        case 2: // Sides +
            if (config.numSides < config.maxSides) {
                initPolygon(config.numSides + 1, window.getSize());
                resetChaosGame();
                if (config.mode == GenerationMode::RecursiveSubdivision) rebuildRecursiveMesh();
            }
            break;
        case 3: // Ratio -
            config.autoJumpRatio = false;
            config.jumpRatio = std::max(0.15f, config.jumpRatio - 0.025f);
            resetChaosGame();
            break;
        case 4: // Ratio +
            config.autoJumpRatio = false;
            config.jumpRatio = std::min(0.85f, config.jumpRatio + 0.025f);
            resetChaosGame();
            break;
        case 5: // Mode Switch
            config.mode = (config.mode == GenerationMode::ChaosGame) 
                        ? GenerationMode::RecursiveSubdivision 
                        : GenerationMode::ChaosGame;
            if (config.mode == GenerationMode::ChaosGame) resetChaosGame();
            else rebuildRecursiveMesh();
            break;
        case 6: // Rule Toggle
            config.noRepeatRule = !config.noRepeatRule;
            resetChaosGame();
            break;
        case 7: // Pause
            config.isPaused = !config.isPaused;
            break;
        case 8: // Reset
            resetChaosGame();
            if (config.mode == GenerationMode::RecursiveSubdivision) rebuildRecursiveMesh();
            break;
        case 9: // Speed -
            if (config.mode == GenerationMode::ChaosGame) {
                if (config.pointsPerFrame > 250) config.pointsPerFrame -= 250;
                else config.pointsPerFrame = 50;
            } else {
                config.recursionDepth = std::max(0, config.recursionDepth - 1);
                rebuildRecursiveMesh();
            }
            break;
        case 10: // Speed +
            if (config.mode == GenerationMode::ChaosGame) {
                config.pointsPerFrame = std::min<size_t>(10000, config.pointsPerFrame + 250);
            } else {
                config.recursionDepth = std::min(config.maxRecursionDepth, config.recursionDepth + 1);
                rebuildRecursiveMesh();
            }
            break;
        case 11: // Size -
            config.pointSize = std::max(1.0f, config.pointSize - 0.5f);
            break;
        case 12: // Size +
            config.pointSize = std::min(6.0f, config.pointSize + 0.5f);
            break;
        case 13: // Color
            config.colorScheme = static_cast<ColorScheme>((static_cast<int>(config.colorScheme) + 1) % 6);
            if (config.mode == GenerationMode::RecursiveSubdivision) rebuildRecursiveMesh();
            else resetChaosGame();
            break;
        case 14: // Console Input
            promptConsoleInput(window);
            break;
        case 15: // Reset Geometry
            config.autoJumpRatio = true;
            initPolygon(config.numSides, window.getSize());
            resetChaosGame();
            if (config.mode == GenerationMode::RecursiveSubdivision) rebuildRecursiveMesh();
            break;
    }
}

// ============================================================================
// 7. Interactive Console Input for Lab Examination
// ============================================================================

void promptConsoleInput(sf::RenderWindow& window) {
    std::cout << "\n=============================================================\n";
    std::cout << "        GENERALIZED N-GON FRACTAL - USER PARAMETER INPUT     \n";
    std::cout << "=============================================================\n";
    std::cout << "Enter Number of Polygon Sides (N between 3 and 12):\n";
    std::cout << "  3 = Triangle (Classic Sierpinski Gasket)\n";
    std::cout << "  4 = Square (Sierpinski Carpet)\n";
    std::cout << "  5 = Pentagon (Dürer's Pentagasket / Golden Ratio)\n";
    std::cout << "  6 = Hexagon (Hexaflake)\n";
    std::cout << "  8 = Octagon (Octaflake)\n";
    std::cout << "Number of Sides [Current: " << config.numSides << "]: ";
    std::string line;
    std::getline(std::cin, line);
    if (!line.empty()) {
        int n = std::stoi(line);
        config.numSides = std::max(config.minSides, std::min(config.maxSides, n));
        config.autoJumpRatio = true;
    }

    std::cout << "Use Optimal Mathematical Jump Ratio (r = " 
              << std::fixed << std::setprecision(3) << computeOptimalJumpRatio(config.numSides)
              << ")? (y/n) [y]: ";
    std::getline(std::cin, line);
    if (!line.empty() && (line[0] == 'n' || line[0] == 'N')) {
        config.autoJumpRatio = false;
        std::cout << "Enter custom jump ratio (0.1 to 0.9) [Current: " << config.jumpRatio << "]: ";
        std::getline(std::cin, line);
        if (!line.empty()) config.jumpRatio = std::stof(line);
    } else {
        config.autoJumpRatio = true;
    }

    std::cout << "Enter Target Total Points [Current: " << config.targetPoints << "]: ";
    std::getline(std::cin, line);
    if (!line.empty()) config.targetPoints = std::stoul(line);

    std::cout << "Enter Points Per Frame / Speed [Current: " << config.pointsPerFrame << "]: ";
    std::getline(std::cin, line);
    if (!line.empty()) config.pointsPerFrame = std::stoul(line);

    std::cout << "Enter Point Size in Pixels [Current: " << config.pointSize << "]: ";
    std::getline(std::cin, line);
    if (!line.empty()) config.pointSize = std::stof(line);

    initPolygon(config.numSides, window.getSize());
    resetChaosGame();

    std::cout << ">> Parameters applied successfully! Returning focus to window.\n\n";
    window.requestFocus();
}

// ============================================================================
// 8. On-Screen HUD Renderer
// ============================================================================

void renderHUD(sf::RenderWindow& window, float fps, sf::Vector2i mousePos) {
    sf::RectangleShape panel(sf::Vector2f(config.controlPanelWidth, static_cast<float>(window.getSize().y)));
    panel.setFillColor(sf::Color(22, 25, 36, 245));
    panel.setOutlineColor(sf::Color(60, 65, 82));
    panel.setOutlineThickness(1.0f);
    window.draw(panel);

    if (!fontLoaded) return;

    sf::Text title;
    title.setFont(hudFont);
    title.setCharacterSize(16);
    title.setStyle(sf::Text::Bold);
    title.setFillColor(sf::Color(0, 220, 255));
    title.setString("N-GON FRACTAL GENERATOR");
    title.setPosition(20.0f, 15.0f);
    window.draw(title);

    sf::Text subtitle;
    subtitle.setFont(hudFont);
    subtitle.setCharacterSize(12);
    subtitle.setFillColor(sf::Color(140, 145, 165));
    subtitle.setString("CGM Lab Project | B.Tech CSE (AI)");
    subtitle.setPosition(20.0f, 38.0f);
    window.draw(subtitle);

    // Live Metrics
    const char* polygonNames[] = {
        "Triangle (Sierpinski)", "Square (Carpet)", "Pentagon (Pentagasket)",
        "Hexagon (Hexaflake)", "Heptagon", "Octagon (Octaflake)",
        "Nonagon", "Decagon", "Hendecagon", "Dodecagon"
    };
    int nameIdx = std::max(0, std::min(9, config.numSides - 3));

    std::ostringstream ss;
    ss << "Shape: " << polygonNames[nameIdx] << " (N=" << config.numSides << ")\n";
    ss << "Jump Ratio (r): " << std::fixed << std::setprecision(3) << config.jumpRatio
       << (config.autoJumpRatio ? " [Auto]" : " [Manual]") << "\n";
    ss << "FPS: " << std::fixed << std::setprecision(1) << fps << "  |  " 
       << (config.isPaused ? "[PAUSED]" : "[RUNNING]") << "\n";
    float pct = (config.targetPoints > 0) ? (100.0f * currentPointCount / config.targetPoints) : 0.0f;
    ss << "Points: " << currentPointCount << " / " << config.targetPoints << " (" << std::fixed << std::setprecision(1) << pct << "%)\n";
    ss << "Speed: " << config.pointsPerFrame << " pts/fr  |  Size: " << config.pointSize << "px";

    sf::Text metrics;
    metrics.setFont(hudFont);
    metrics.setCharacterSize(12);
    metrics.setFillColor(sf::Color(220, 224, 235));
    metrics.setString(ss.str());
    metrics.setPosition(20.0f, 60.0f);
    window.draw(metrics);

    // Separator line
    sf::RectangleShape line(sf::Vector2f(config.controlPanelWidth - 40.0f, 1.0f));
    line.setFillColor(sf::Color(55, 60, 78));
    line.setPosition(20.0f, 138.0f);
    window.draw(line);

    // Render interactive buttons
    sf::Vector2f mouseFloat(static_cast<float>(mousePos.x), static_cast<float>(mousePos.y));

    for (auto& btn : guiButtons) {
        bool hovered = btn.bounds.contains(mouseFloat);

        sf::RectangleShape box(sf::Vector2f(btn.bounds.width, btn.bounds.height));
        box.setPosition(btn.bounds.left, btn.bounds.top);

        if (hovered) {
            box.setFillColor(sf::Color(55, 65, 92));
            box.setOutlineColor(sf::Color(0, 200, 255));
        } else {
            box.setFillColor(sf::Color(36, 40, 56));
            box.setOutlineColor(sf::Color(65, 72, 95));
        }
        box.setOutlineThickness(1.2f);
        window.draw(box);

        std::string labelStr = btn.label;
        if (btn.id == 1) labelStr = "Sides - (" + std::to_string(config.numSides) + ")";
        else if (btn.id == 2) labelStr = "Sides + (" + std::to_string(config.numSides) + ")";
        else if (btn.id == 5) labelStr = (config.mode == GenerationMode::ChaosGame) ? "Mode: Chaos" : "Mode: Recursive";
        else if (btn.id == 6) labelStr = config.noRepeatRule ? "Rule: No-Repeat" : "Rule: Standard";
        else if (btn.id == 7) labelStr = config.isPaused ? "Resume [Space]" : "Pause [Space]";
        else if (btn.id == 13) {
            const char* schemeNames[] = { "IFS Vertex Palette", "Solid Cyan", "Solid Lime", "Solid Amber", "Height Gradient", "Rainbow Hue" };
            labelStr = "Color: " + std::string(schemeNames[static_cast<int>(config.colorScheme)]);
        }

        sf::Text btnText;
        btnText.setFont(hudFont);
        btnText.setCharacterSize(11);
        btnText.setFillColor(hovered ? sf::Color::White : sf::Color(210, 215, 230));
        btnText.setString(labelStr);

        sf::FloatRect tb = btnText.getLocalBounds();
        btnText.setPosition(
            btn.bounds.left + (btn.bounds.width - tb.width) / 2.0f,
            btn.bounds.top + (btn.bounds.height - tb.height) / 2.0f - 2.0f
        );
        window.draw(btnText);
    }

    // Guide Header
    float guideY = 475.0f;
    sf::Text guideHeader;
    guideHeader.setFont(hudFont);
    guideHeader.setCharacterSize(13);
    guideHeader.setStyle(sf::Text::Bold);
    guideHeader.setFillColor(sf::Color(255, 200, 50));
    guideHeader.setString("INTERACTIVE INPUT GUIDE:");
    guideHeader.setPosition(20.0f, guideY);
    window.draw(guideHeader);

    std::ostringstream gs;
    gs << "* INPUT SIDES (N): Press [N] or click\n"
       << "  'Sides +/-' to change polygon sides!\n\n"
       << "* DRAG VERTICES: Click and drag any\n"
       << "  of the " << config.numSides << " vertices to morph the shape!\n\n"
       << "* CLICK CANVAS: Click in drawing area\n"
       << "  to set custom starting seed (P0)!\n\n"
       << "KEYBOARD SHORTCUTS:\n"
       << " [N] Sides +       [Shift+N] Sides -\n"
       << " [Space] Pause     [R] Reset\n"
       << " [C] Color Palette [I] Console Input\n"
       << " [Up/Dn] Speed     [+/-] Size\n\n"
       << "HAUSDORFF DIMENSION (N=3):\n"
       << " D = log(3)/log(2) ~ 1.585";

    sf::Text guideText;
    guideText.setFont(hudFont);
    guideText.setCharacterSize(11);
    guideText.setFillColor(sf::Color(175, 182, 200));
    guideText.setString(gs.str());
    guideText.setPosition(20.0f, guideY + 22.0f);
    window.draw(guideText);
}

// ============================================================================
// 9. Main Application Loop
// ============================================================================

int main(int argc, char* argv[]) {
    // Check font
    std::vector<std::string> fontCandidates = {
        "arial.ttf", "C:\\Windows\\Fonts\\arial.ttf", "C:\\Windows\\Fonts\\segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/Library/Fonts/Arial.ttf"
    };
    for (const auto& path : fontCandidates) {
        FILE* f = std::fopen(path.c_str(), "rb");
        if (f) {
            std::fclose(f);
            if (hudFont.loadFromFile(path)) {
                fontLoaded = true;
                break;
            }
        }
    }

    setupButtons();

    sf::ContextSettings settings;
    settings.antialiasingLevel = 4;

    sf::RenderWindow window(
        sf::VideoMode(config.windowWidth, config.windowHeight),
        "Generalized N-Gon Fractal Generator [CGM Lab Project - B.Tech CSE AI]",
        sf::Style::Titlebar | sf::Style::Close,
        settings
    );
    window.setFramerateLimit(60);

    initPolygon(config.numSides, window.getSize());
    resetChaosGame();
    rebuildRecursiveMesh();

    if (argc > 1 && std::string(argv[1]) == "--input") {
        promptConsoleInput(window);
    }

    sf::Clock fpsClock;
    float currentFps = 60.0f;
    int frameCounter = 0;

    while (window.isOpen()) {
        frameCounter++;
        if (fpsClock.getElapsedTime().asSeconds() >= 0.5f) {
            currentFps = frameCounter / fpsClock.restart().asSeconds();
            frameCounter = 0;
        }

        sf::Vector2i mousePixelPos = sf::Mouse::getPosition(window);
        sf::Vector2f mousePos(static_cast<float>(mousePixelPos.x), static_cast<float>(mousePixelPos.y));

        // Detect hover over polygon vertices
        hoveredVertex = -1;
        for (size_t i = 0; i < polygonVertices.size(); ++i) {
            float dx = mousePos.x - polygonVertices[i].x;
            float dy = mousePos.y - polygonVertices[i].y;
            if (std::sqrt(dx * dx + dy * dy) <= 16.0f) {
                hoveredVertex = static_cast<int>(i);
                break;
            }
        }

        // --------------------------------------------------------------------
        // Event Handling
        // --------------------------------------------------------------------
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) window.close();

            // MOUSE BUTTON PRESSED
            if (event.type == sf::Event::MouseButtonPressed && event.mouseButton.button == sf::Mouse::Left) {
                sf::Vector2f clickPos(static_cast<float>(event.mouseButton.x), static_cast<float>(event.mouseButton.y));

                bool clickedButton = false;
                for (const auto& btn : guiButtons) {
                    if (btn.bounds.contains(clickPos)) {
                        handleButtonClick(btn.id, window);
                        clickedButton = true;
                        break;
                    }
                }

                if (!clickedButton) {
                    if (hoveredVertex != -1) {
                        draggedVertex = hoveredVertex;
                    } else if (clickPos.x > config.controlPanelWidth) {
                        currentChaosPoint = clickPos;
                        resetChaosGame(true);
                    }
                }
            }

            // MOUSE BUTTON RELEASED
            if (event.type == sf::Event::MouseButtonReleased && event.mouseButton.button == sf::Mouse::Left) {
                draggedVertex = -1;
            }

            // MOUSE MOVED (DRAGGING VERTEX)
            if (event.type == sf::Event::MouseMoved && draggedVertex != -1) {
                float clampedX = std::max(config.controlPanelWidth + 20.0f, std::min(static_cast<float>(window.getSize().x) - 20.0f, mousePos.x));
                float clampedY = std::max(20.0f, std::min(static_cast<float>(window.getSize().y) - 20.0f, mousePos.y));
                polygonVertices[draggedVertex] = sf::Vector2f(clampedX, clampedY);

                if (config.mode == GenerationMode::ChaosGame) {
                    resetChaosGame(true);
                } else {
                    rebuildRecursiveMesh();
                }
            }

            // KEYBOARD SHORTCUTS
            if (event.type == sf::Event::KeyPressed) {
                // [N] key for sides
                if (event.key.code == sf::Keyboard::N) {
                    if (event.key.shift) handleButtonClick(1, window); // Sides -
                    else handleButtonClick(2, window);                // Sides +
                }
                else if (event.key.code == sf::Keyboard::Space) config.isPaused = !config.isPaused;
                else if (event.key.code == sf::Keyboard::M) handleButtonClick(5, window);
                else if (event.key.code == sf::Keyboard::R) handleButtonClick(8, window);
                else if (event.key.code == sf::Keyboard::C) handleButtonClick(13, window);
                else if (event.key.code == sf::Keyboard::Up) handleButtonClick(10, window);
                else if (event.key.code == sf::Keyboard::Down) handleButtonClick(9, window);
                else if (event.key.code == sf::Keyboard::Add || event.key.code == sf::Keyboard::Equal) handleButtonClick(12, window);
                else if (event.key.code == sf::Keyboard::Subtract || event.key.code == sf::Keyboard::Dash) handleButtonClick(11, window);
                else if (event.key.code == sf::Keyboard::I) promptConsoleInput(window);
            }
        }

        // --------------------------------------------------------------------
        // Simulation Step
        // --------------------------------------------------------------------
        if (config.mode == GenerationMode::ChaosGame && !config.isPaused) {
            chaosGameStep(config.pointsPerFrame);
        }

        // --------------------------------------------------------------------
        // Rendering
        // --------------------------------------------------------------------
        window.clear(sf::Color(18, 18, 24));

        // Draw polygon perimeter wireframe
        if (!polygonVertices.empty()) {
            sf::VertexArray perimeter(sf::LineStrip, polygonVertices.size() + 1);
            for (size_t i = 0; i < polygonVertices.size(); ++i) {
                perimeter[i].position = polygonVertices[i];
                perimeter[i].color = sf::Color(65, 70, 90);
            }
            perimeter[polygonVertices.size()].position = polygonVertices[0];
            perimeter[polygonVertices.size()].color = sf::Color(65, 70, 90);
            window.draw(perimeter);
        }

        // Draw fractal
        if (config.mode == GenerationMode::ChaosGame) {
            sf::Sprite canvasSprite(chaosCanvas.getTexture());
            window.draw(canvasSprite);

            // Roaming point tracker
            sf::CircleShape tracker(4.0f);
            tracker.setOrigin(4.0f, 4.0f);
            tracker.setPosition(currentChaosPoint);
            tracker.setFillColor(sf::Color(255, 230, 80));
            tracker.setOutlineColor(sf::Color::White);
            tracker.setOutlineThickness(1.5f);
            window.draw(tracker);
        } else {
            if (config.wireframeMode) window.draw(recursiveLines);
            else window.draw(recursiveTriangles);
        }

        // Draw corner vertices with interactive drag handles
        for (size_t i = 0; i < polygonVertices.size(); ++i) {
            bool isHover = (hoveredVertex == static_cast<int>(i) || draggedVertex == static_cast<int>(i));
            float r = isHover ? 8.0f : 6.0f;

            if (isHover) {
                sf::CircleShape halo(16.0f);
                halo.setOrigin(16.0f, 16.0f);
                halo.setPosition(polygonVertices[i]);
                halo.setFillColor(sf::Color(255, 255, 255, 40));
                halo.setOutlineColor(sf::Color(0, 220, 255, 200));
                halo.setOutlineThickness(1.5f);
                window.draw(halo);
            }

            sf::CircleShape anchor(r);
            anchor.setOrigin(r, r);
            anchor.setPosition(polygonVertices[i]);
            anchor.setFillColor(evaluateColor(polygonVertices[i], static_cast<int>(i), 0));
            anchor.setOutlineColor(sf::Color::White);
            anchor.setOutlineThickness(1.5f);
            window.draw(anchor);
        }

        // Draw UI Overlay
        renderHUD(window, currentFps, mousePixelPos);

        window.display();
    }

    return 0;
}
