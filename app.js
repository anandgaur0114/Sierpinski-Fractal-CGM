/**
 * ============================================================================
 * FractalWave — 5G & IoT Multiband Fractal Antenna Engineering Suite
 * Computer Graphics & Multimedia (CGM) Lab Project — B.Tech CSE (AI)
 * 
 * Features:
 *   1. Dual Simulation Engine:
 *      - Stochastic Chaos Game (Iterated Function Systems / N-Flakes)
 *      - Deterministic Recursive Subdivision
 *   2. Real-World Engineering Problem Solutions:
 *      - Multiband 5G/IoT Fractal Antenna RF Spectrum Simulator (S11 Return Loss)
 *      - Micro-Channel Thermal Heat Dissipation Analyzer (Perimeter Paradox)
 *   3. Interactive Human-Computer Interaction:
 *      - Mouse dragging of all N polygon vertices in real time
 *      - Click-to-seed starting coordinate P0
 *   4. GPU-Style 60 FPS Double-Buffering with Off-screen HTML5 Canvas
 * ============================================================================
 */

(function () {
  'use strict';

  // -------------------------------------------------------------
  // CONFIGURATION & GLOBAL STATE
  // -------------------------------------------------------------
  const state = {
    // Mode: 'chaos' or 'recursive'
    mode: 'chaos',
    numSides: 3,
    jumpRatio: 0.5,
    autoJumpRatio: true,
    noRepeatRule: false,
    speed: 2500, // points generated per frame
    pointSize: 1.5,
    colorTheme: 'ifs',
    targetPoints: 100000,
    currentPoints: 0,
    isPaused: false,

    // Recursive Subdivision
    recursionDepth: 4,
    wireframeMode: false,

    // Real-Life 5G Antenna Parameters
    patchSizeMm: 60, // L0 in millimeters
    dielectricEr: 4.4, // FR-4 default
    antennaDepth: 3,

    // Geometry
    polygonVertices: [],
    draggedVertexIdx: -1,
    hoveredVertexIdx: -1,
    currentPoint: { x: 0, y: 0 },
    lastChosenVertex: -1,

    // FPS Telemetry
    fps: 60.0,
    frameCount: 0,
    lastTime: performance.now()
  };

  // DOM Elements
  const canvas = document.getElementById('fractalCanvas');
  const ctx = canvas.getContext('2d');
  const spectrumCanvas = document.getElementById('spectrumCanvas');
  const specCtx = spectrumCanvas.getContext('2d');
  const canvasWrapper = document.getElementById('canvasWrapper');

  // Off-screen canvas accumulator (emulates C++ sf::RenderTexture)
  const offscreenCanvas = document.createElement('canvas');
  const offscreenCtx = offscreenCanvas.getContext('2d');

  // UI Readouts
  const topStatus = document.getElementById('topStatus');
  const topFps = document.getElementById('topFps');
  const topPointCount = document.getElementById('topPointCount');
  const topResonantBands = document.getElementById('topResonantBands');
  const canvasModeLabel = document.getElementById('canvasModeLabel');
  const tagDimensions = document.getElementById('tagDimensions');
  const tagRatio = document.getElementById('tagRatio');
  const frequencyChips = document.getElementById('frequencyChips');

  // Sliders and Selects
  const numSidesSlider = document.getElementById('numSidesSlider');
  const numSidesVal = document.getElementById('numSidesVal');
  const jumpRatioSlider = document.getElementById('jumpRatioSlider');
  const jumpRatioVal = document.getElementById('jumpRatioVal');
  const chkAutoRatio = document.getElementById('chkAutoRatio');
  const chkNoRepeatRule = document.getElementById('chkNoRepeatRule');
  const speedSlider = document.getElementById('speedSlider');
  const speedVal = document.getElementById('speedVal');
  const pointSizeSlider = document.getElementById('pointSizeSlider');
  const pointSizeVal = document.getElementById('pointSizeVal');
  const colorThemeSelect = document.getElementById('colorThemeSelect');

  const antennaPatchSelect = document.getElementById('antennaPatchSelect');
  const substrateSelect = document.getElementById('substrateSelect');
  const patchSizeSlider = document.getElementById('patchSizeSlider');
  const patchSizeVal = document.getElementById('patchSizeVal');
  const antennaDepthSlider = document.getElementById('antennaDepthSlider');
  const antennaDepthVal = document.getElementById('antennaDepthVal');

  // Action Buttons
  const btnPlayPause = document.getElementById('btnPlayPause');
  const btnResetSimulation = document.getElementById('btnResetSimulation');
  const btnResetGeometry = document.getElementById('btnResetGeometry');
  const btnExportSnapshot = document.getElementById('btnExportSnapshot');
  const btnPresentationModal = document.getElementById('btnPresentationModal');
  const btnCloseModal = document.getElementById('btnCloseModal');
  const presentationModal = document.getElementById('presentationModal');

  // -------------------------------------------------------------
  // MATHEMATICAL FUNCTIONS
  // -------------------------------------------------------------
  
  /**
   * Calculates the optimal contraction ratio r(N) for regular N-gons:
   * r(N) = 1 / [ 2 * (1 + sum_{k=1}^{floor(N/4)} cos(2*pi*k / N)) ]
   */
  function computeOptimalJumpRatio(n) {
    if (n <= 3) return 0.5;
    if (n === 4) return 0.5; // with non-adjacent rule => Sierpinski Carpet
    let sumCos = 0.0;
    const limit = Math.floor(n / 4);
    for (let k = 1; k <= limit; ++k) {
      sumCos += Math.cos((2.0 * Math.PI * k) / n);
    }
    return 1.0 / (2.0 * (1.0 + sumCos));
  }

  /**
   * Calculates Hausdorff Dimension D = ln(N) / ln(1/s)
   */
  function computeHausdorffDimension(n, r) {
    if (r <= 0 || r >= 1) return 'N/A';
    const s = r;
    const d = Math.log(n) / Math.log(1.0 / s);
    return d.toFixed(4);
  }

  /**
   * Generates N distinct HSL colors for IFS Affine Map decomposition
   */
  function getVertexColor(index, total) {
    const hue = (index / total) * 360;
    return `hsl(${hue}, 85%, 60%)`;
  }

  /**
   * Evaluates point color based on active color theme
   */
  function evaluatePointColor(x, y, chosenVertexIdx, pointIndex) {
    switch (state.colorTheme) {
      case 'ifs':
        return getVertexColor(chosenVertexIdx, state.numSides);
      case 'cyan':
        return '#00f0ff';
      case 'lime':
        return '#23e882';
      case 'amber':
        return '#fca311';
      case 'gradient': {
        const minY = Math.min(...state.polygonVertices.map(v => v.y));
        const maxY = Math.max(...state.polygonVertices.map(v => v.y));
        const t = Math.max(0, Math.min(1, (y - minY) / (maxY - minY || 1)));
        const r = Math.round((1 - t) * 255 + t * 138);
        const g = Math.round((1 - t) * 215 + t * 43);
        const b = Math.round((1 - t) * 30 + t * 226);
        return `rgb(${r},${g},${b})`;
      }
      case 'rainbow': {
        const hue = (pointIndex * 0.15) % 360;
        return `hsl(${hue}, 90%, 60%)`;
      }
      default:
        return '#00f0ff';
    }
  }

  // -------------------------------------------------------------
  // GEOMETRY & RESIZING INITIALIZATION
  // -------------------------------------------------------------
  function resizeCanvases() {
    const rect = canvasWrapper.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;

    offscreenCanvas.width = canvas.width;
    offscreenCanvas.height = canvas.height;

    // Scale spectrum canvas
    const specRect = spectrumCanvas.parentElement.getBoundingClientRect();
    spectrumCanvas.width = specRect.width * dpr;
    spectrumCanvas.height = specRect.height * dpr;
    spectrumCanvas.style.width = `${specRect.width}px`;
    spectrumCanvas.style.height = `${specRect.height}px`;

    initPolygonVertices();
    resetSimulation(false);
  }

  function initPolygonVertices() {
    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const padding = 60 * (window.devicePixelRatio || 1);
    const radius = Math.min(centerX, centerY) - padding;

    if (state.autoJumpRatio) {
      state.jumpRatio = computeOptimalJumpRatio(state.numSides);
      jumpRatioSlider.value = state.jumpRatio.toFixed(3);
      jumpRatioVal.textContent = `${state.jumpRatio.toFixed(3)} [Auto]`;
    }

    if (state.numSides === 4) {
      state.noRepeatRule = true;
      chkNoRepeatRule.checked = true;
    }

    state.polygonVertices = [];
    for (let i = 0; i < state.numSides; i++) {
      // Offset by -pi/2 so top vertex points vertically
      const angle = -Math.PI / 2 + (2 * Math.PI * i) / state.numSides;
      state.polygonVertices.push({
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      });
    }

    updateHeaderBadges();
    updateRFPhysics();
  }

  function resetSimulation(keepSeedPoint = false) {
    // Clear off-screen accumulator buffer
    offscreenCtx.fillStyle = '#0b0f14';
    offscreenCtx.fillRect(0, 0, offscreenCanvas.width, offscreenCanvas.height);

    state.currentPoints = 0;
    state.lastChosenVertex = -1;

    if (!keepSeedPoint && state.polygonVertices.length > 0) {
      const minX = Math.min(...state.polygonVertices.map(v => v.x));
      const maxX = Math.max(...state.polygonVertices.map(v => v.x));
      const minY = Math.min(...state.polygonVertices.map(v => v.y));
      const maxY = Math.max(...state.polygonVertices.map(v => v.y));

      state.currentPoint = {
        x: minX + Math.random() * (maxX - minX),
        y: minY + Math.random() * (maxY - minY)
      };
    }

    // Warmup iterations: discard initial 25 points so point contracts into attractor
    const r = state.jumpRatio;
    for (let i = 0; i < 30; i++) {
      let vIdx = Math.floor(Math.random() * state.numSides);
      if (state.noRepeatRule && vIdx === state.lastChosenVertex) {
        vIdx = (vIdx + 1) % state.numSides;
      }
      state.lastChosenVertex = vIdx;
      const targetV = state.polygonVertices[vIdx];
      state.currentPoint.x = (1 - r) * state.currentPoint.x + r * targetV.x;
      state.currentPoint.y = (1 - r) * state.currentPoint.y + r * targetV.y;
    }

    topPointCount.textContent = `0 / ${state.targetPoints.toLocaleString()}`;
  }

  // -------------------------------------------------------------
  // SIMULATION ENGINES: CHAOS GAME & RECURSIVE SUBDIVISION
  // -------------------------------------------------------------
  
  /**
   * Chaos Game Batch Step (Stochastic Point Generation)
   */
  function chaosGameStep(batchCount) {
    if (state.currentPoints >= state.targetPoints) return;
    const actual = Math.min(batchCount, state.targetPoints - state.currentPoints);
    if (actual <= 0) return;

    const r = state.jumpRatio;
    const pSize = state.pointSize * (window.devicePixelRatio || 1);
    const halfSize = pSize / 2;

    for (let i = 0; i < actual; i++) {
      let vIdx = Math.floor(Math.random() * state.numSides);
      if (state.noRepeatRule && vIdx === state.lastChosenVertex) {
        vIdx = (vIdx + 1 + Math.floor(Math.random() * (state.numSides - 1))) % state.numSides;
      }
      state.lastChosenVertex = vIdx;

      const targetV = state.polygonVertices[vIdx];
      state.currentPoint.x = (1 - r) * state.currentPoint.x + r * targetV.x;
      state.currentPoint.y = (1 - r) * state.currentPoint.y + r * targetV.y;

      const color = evaluatePointColor(state.currentPoint.x, state.currentPoint.y, vIdx, state.currentPoints + i);
      offscreenCtx.fillStyle = color;

      if (pSize <= 1.5) {
        offscreenCtx.fillRect(state.currentPoint.x, state.currentPoint.y, pSize, pSize);
      } else {
        offscreenCtx.beginPath();
        offscreenCtx.arc(state.currentPoint.x, state.currentPoint.y, halfSize, 0, Math.PI * 2);
        offscreenCtx.fill();
      }
    }

    state.currentPoints += actual;
    topPointCount.textContent = `${state.currentPoints.toLocaleString()} / ${state.targetPoints.toLocaleString()}`;
  }

  /**
   * Recursive Subdivision (Deterministic Triangle Splitting)
   */
  function drawRecursive(targetCtx) {
    if (state.polygonVertices.length < 3) return;

    function subdivide(p1, p2, p3, depth) {
      if (depth <= 0) {
        targetCtx.beginPath();
        targetCtx.moveTo(p1.x, p1.y);
        targetCtx.lineTo(p2.x, p2.y);
        targetCtx.lineTo(p3.x, p3.y);
        targetCtx.closePath();

        if (!state.wireframeMode) {
          targetCtx.fillStyle = 'rgba(0, 240, 255, 0.45)';
          targetCtx.fill();
        }
        targetCtx.strokeStyle = '#00f0ff';
        targetCtx.lineWidth = 1.2 * (window.devicePixelRatio || 1);
        targetCtx.stroke();
        return;
      }

      const m12 = { x: 0.5 * (p1.x + p2.x), y: 0.5 * (p1.y + p2.y) };
      const m23 = { x: 0.5 * (p2.x + p3.x), y: 0.5 * (p2.y + p3.y) };
      const m31 = { x: 0.5 * (p3.x + p1.x), y: 0.5 * (p3.y + p1.y) };

      subdivide(p1, m12, m31, depth - 1);
      subdivide(m12, p2, m23, depth - 1);
      subdivide(m31, m23, p3, depth - 1);
    }

    subdivide(state.polygonVertices[0], state.polygonVertices[1], state.polygonVertices[2], state.recursionDepth);
  }

  // -------------------------------------------------------------
  // REAL-WORLD 5G FRACTAL ANTENNA PHYSICS ENGINE
  // -------------------------------------------------------------
  let resonantFrequencies = [];

  function updateRFPhysics() {
    const c = 3.0e8; // speed of light in m/s
    const L0_meters = (state.patchSizeMm / 1000.0);
    const er = state.dielectricEr;
    
    // Effective dielectric constant for microstrip patch
    const er_eff = (er + 1) / 2 + ((er - 1) / 2) * (1 / Math.sqrt(1 + 12 * (0.0016 / 0.05)));
    
    // Fundamental resonant frequency f0 (in GHz)
    const f0 = (c / (2 * L0_meters * Math.sqrt(er_eff))) / 1e9;

    // Contraction ratio scale factor delta = 1 / r
    const delta = 1.0 / state.jumpRatio;
    
    resonantFrequencies = [];
    const bandLabels = [
      { name: 'Band 1 (Fundamental GSM)', freq: f0 },
      { name: 'Band 2 (4G LTE / GPS)', freq: f0 * delta * 0.95 },
      { name: 'Band 3 (Wi-Fi 6 / 5G Sub-6)', freq: f0 * Math.pow(delta, 2) * 0.90 },
      { name: 'Band 4 (High 5G mmWave)', freq: f0 * Math.pow(delta, 3) * 0.85 }
    ];

    bandLabels.forEach((b, idx) => {
      if (idx <= state.antennaDepth) {
        resonantFrequencies.push({
          label: b.name,
          freq: parseFloat(b.freq.toFixed(2))
        });
      }
    });

    // Update UI chips
    frequencyChips.innerHTML = '';
    resonantFrequencies.forEach(rf => {
      const chip = document.createElement('div');
      chip.className = 'band-chip active';
      chip.innerHTML = `<span class="dot"></span><strong>${rf.freq} GHz</strong> — ${rf.label}`;
      frequencyChips.appendChild(chip);
    });

    // Update telemetry metrics
    const reduction = (1 - (1 / Math.pow(state.numSides, state.antennaDepth * 0.5))) * 100;
    document.getElementById('statSizeReduction').textContent = `-${reduction.toFixed(1)}%`;
    topResonantBands.textContent = `${resonantFrequencies.length} Resonant Bands`;

    // Thermal metrics
    const k = state.antennaDepth;
    const relArea = Math.pow(3 / 4, k) * 100;
    const relPerimeter = Math.pow(3 / 2, k) * 100;
    document.getElementById('thermalStep').textContent = `Iteration k = ${k}`;
    document.getElementById('thermalArea').textContent = `${relArea.toFixed(1)}% (Excised to 0)`;
    document.getElementById('thermalPerimeter').textContent = `+${relPerimeter.toFixed(1)}% (Perimeter Paradox)`;
    document.getElementById('thermalCooling').textContent = `+${(relPerimeter * 0.75).toFixed(0)}% Surface Dissipation`;

    drawSpectrumGraph();
  }

  /**
   * Draws live S11 Return Loss (dB) vs. Frequency (GHz) Spectrum Graph
   */
  function drawSpectrumGraph() {
    const w = spectrumCanvas.width;
    const h = spectrumCanvas.height;
    specCtx.clearRect(0, 0, w, h);

    const padLeft = 45 * (window.devicePixelRatio || 1);
    const padRight = 20 * (window.devicePixelRatio || 1);
    const padTop = 15 * (window.devicePixelRatio || 1);
    const padBottom = 25 * (window.devicePixelRatio || 1);

    const plotW = w - padLeft - padRight;
    const plotH = h - padTop - padBottom;

    const minFreq = 0.5; // GHz
    const maxFreq = 30.0; // GHz
    const minDb = -30.0;
    const maxDb = 0.0;

    // Grid lines & labels
    specCtx.strokeStyle = '#21262d';
    specCtx.lineWidth = 1;
    specCtx.font = `${10 * (window.devicePixelRatio || 1)}px JetBrains Mono`;
    specCtx.fillStyle = '#6e7681';

    // Horizontal dB lines (-10dB threshold highlighted)
    for (let db = 0; db >= -30; db -= 5) {
      const y = padTop + ((maxDb - db) / (maxDb - minDb)) * plotH;
      specCtx.beginPath();
      specCtx.moveTo(padLeft, y);
      specCtx.lineTo(w - padRight, y);

      if (db === -10) {
        specCtx.strokeStyle = 'rgba(35, 232, 130, 0.4)';
        specCtx.setLineDash([4, 4]);
        specCtx.stroke();
        specCtx.setLineDash([]);
        specCtx.fillStyle = '#23e882';
        specCtx.fillText('-10dB PASS', padLeft + 6, y - 4);
        specCtx.fillStyle = '#6e7681';
        specCtx.strokeStyle = '#21262d';
      } else {
        specCtx.stroke();
      }
      specCtx.fillText(`${db}dB`, 8, y + 4);
    }

    // Vertical Frequency lines
    for (let f = 5; f <= 30; f += 5) {
      const x = padLeft + ((f - minFreq) / (maxFreq - minFreq)) * plotW;
      specCtx.beginPath();
      specCtx.moveTo(x, padTop);
      specCtx.lineTo(x, h - padBottom);
      specCtx.stroke();
      specCtx.fillText(`${f}G`, x - 8, h - 8);
    }

    // Calculate S11 curve
    specCtx.beginPath();
    specCtx.strokeStyle = '#00f0ff';
    specCtx.lineWidth = 2.0 * (window.devicePixelRatio || 1);

    for (let px = 0; px <= plotW; px += 2) {
      const freq = minFreq + (px / plotW) * (maxFreq - minFreq);
      
      // Base non-resonant reflection is around -2dB
      let s11 = -2.5;

      // Resonant dips (Lorentzian transmission loss peaks)
      resonantFrequencies.forEach(rf => {
        const deltaF = freq - rf.freq;
        const q = 0.8; // bandwidth factor
        const dipDepth = 24.0; // dB drop
        s11 -= dipDepth / (1.0 + Math.pow(deltaF / q, 2));
      });

      // Clamp between min and max
      s11 = Math.max(minDb, Math.min(maxDb, s11));
      const py = padTop + ((maxDb - s11) / (maxDb - minDb)) * plotH;

      if (px === 0) specCtx.moveTo(padLeft + px, py);
      else specCtx.lineTo(padLeft + px, py);
    }
    specCtx.stroke();

    // Mark resonant dip points with glowing markers
    resonantFrequencies.forEach(rf => {
      if (rf.freq >= minFreq && rf.freq <= maxFreq) {
        const x = padLeft + ((rf.freq - minFreq) / (maxFreq - minFreq)) * plotW;
        const dipDb = -26.5;
        const y = padTop + ((maxDb - dipDb) / (maxDb - minDb)) * plotH;

        specCtx.fillStyle = '#23e882';
        specCtx.beginPath();
        specCtx.arc(x, y, 4 * (window.devicePixelRatio || 1), 0, Math.PI * 2);
        specCtx.fill();

        specCtx.fillStyle = '#23e882';
        specCtx.fillText(`${rf.freq}G`, x - 12, y - 8);
      }
    });
  }

  // -------------------------------------------------------------
  // ANIMATION & RENDER LOOP
  // -------------------------------------------------------------
  function renderLoop() {
    // 1. Simulation Step
    if (!state.isPaused) {
      if (state.mode === 'chaos') {
        chaosGameStep(state.speed);
      }
    }

    // 2. Render to Screen Viewport
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (state.mode === 'chaos') {
      // Blit persistent accumulated canvas in 1 draw call
      ctx.drawImage(offscreenCanvas, 0, 0);

      // Draw wandering point tracker
      ctx.fillStyle = '#ffe650';
      ctx.beginPath();
      ctx.arc(state.currentPoint.x, state.currentPoint.y, 4 * (window.devicePixelRatio || 1), 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    } else {
      drawRecursive(ctx);
    }

    // Draw boundary perimeter wireframe
    if (state.polygonVertices.length > 0) {
      ctx.beginPath();
      ctx.moveTo(state.polygonVertices[0].x, state.polygonVertices[0].y);
      for (let i = 1; i < state.polygonVertices.length; i++) {
        ctx.lineTo(state.polygonVertices[i].x, state.polygonVertices[i].y);
      }
      ctx.closePath();
      ctx.strokeStyle = 'rgba(70, 75, 95, 0.7)';
      ctx.lineWidth = 1.5 * (window.devicePixelRatio || 1);
      ctx.stroke();
    }

    // Draw interactive corner vertices with glowing halo on hover/drag
    for (let i = 0; i < state.polygonVertices.length; i++) {
      const v = state.polygonVertices[i];
      const isHover = (i === state.hoveredVertexIdx || i === state.draggedVertexIdx);
      const r = (isHover ? 8 : 6) * (window.devicePixelRatio || 1);

      if (isHover) {
        ctx.beginPath();
        ctx.arc(v.x, v.y, 16 * (window.devicePixelRatio || 1), 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0, 240, 255, 0.2)';
        ctx.fill();
        ctx.strokeStyle = '#00f0ff';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }

      ctx.beginPath();
      ctx.arc(v.x, v.y, r, 0, Math.PI * 2);
      ctx.fillStyle = getVertexColor(i, state.numSides);
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    // 3. FPS Telemetry Calculation
    state.frameCount++;
    const now = performance.now();
    if (now - state.lastTime >= 500) {
      state.fps = (state.frameCount / ((now - state.lastTime) / 1000)).toFixed(1);
      topFps.textContent = state.fps;
      state.frameCount = 0;
      state.lastTime = now;
    }

    requestAnimationFrame(renderLoop);
  }

  // -------------------------------------------------------------
  // USER INTERACTION: MOUSE DRAG & CLICK-TO-SEED
  // -------------------------------------------------------------
  function getCanvasMousePos(e) {
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    return {
      x: (e.clientX - rect.left) * dpr,
      y: (e.clientY - rect.top) * dpr
    };
  }

  canvas.addEventListener('mousemove', (e) => {
    const m = getCanvasMousePos(e);

    // If dragging a vertex, update coordinate
    if (state.draggedVertexIdx !== -1) {
      state.polygonVertices[state.draggedVertexIdx].x = m.x;
      state.polygonVertices[state.draggedVertexIdx].y = m.y;
      resetSimulation(true);
      updateRFPhysics();
      return;
    }

    // Hover detection over vertices
    state.hoveredVertexIdx = -1;
    const threshold = 18 * (window.devicePixelRatio || 1);
    for (let i = 0; i < state.polygonVertices.length; i++) {
      const v = state.polygonVertices[i];
      const dist = Math.hypot(m.x - v.x, m.y - v.y);
      if (dist <= threshold) {
        state.hoveredVertexIdx = i;
        canvas.style.cursor = 'grab';
        break;
      }
    }
    if (state.hoveredVertexIdx === -1) {
      canvas.style.cursor = 'crosshair';
    }
  });

  canvas.addEventListener('mousedown', (e) => {
    const m = getCanvasMousePos(e);
    if (state.hoveredVertexIdx !== -1) {
      state.draggedVertexIdx = state.hoveredVertexIdx;
      canvas.style.cursor = 'grabbing';
    } else {
      // Click-to-seed: set custom starting point P0
      state.currentPoint = { x: m.x, y: m.y };
      resetSimulation(true);
    }
  });

  window.addEventListener('mouseup', () => {
    state.draggedVertexIdx = -1;
    canvas.style.cursor = 'crosshair';
  });

  // -------------------------------------------------------------
  // UI EVENT HANDLERS & BADGES
  // -------------------------------------------------------------
  function updateHeaderBadges() {
    const names = [
      'Triangle (Sierpinski Gasket)', 'Square (Sierpinski Carpet)',
      'Pentagon (Dürer Pentagasket)', 'Hexagon (Hexaflake)',
      'Heptagon', 'Octagon (Octaflake)', 'Nonagon', 'Decagon', 'Hendecagon', 'Dodecagon'
    ];
    const nameStr = names[state.numSides - 3] || `Regular ${state.numSides}-Gon`;
    canvasModeLabel.textContent = `Fractal Viewport — ${nameStr} (N=${state.numSides})`;
    tagDimensions.textContent = `D = ${computeHausdorffDimension(state.numSides, state.jumpRatio)} (Hausdorff)`;
    tagRatio.textContent = `r = ${state.jumpRatio.toFixed(3)}`;
  }

  // Polygon Sides Slider
  numSidesSlider.addEventListener('input', (e) => {
    state.numSides = parseInt(e.target.value, 10);
    numSidesVal.textContent = `N = ${state.numSides}`;
    initPolygonVertices();
    resetSimulation(false);
  });

  // Jump Ratio Slider
  jumpRatioSlider.addEventListener('input', (e) => {
    state.jumpRatio = parseFloat(e.target.value);
    state.autoJumpRatio = false;
    chkAutoRatio.checked = false;
    jumpRatioVal.textContent = state.jumpRatio.toFixed(3);
    updateHeaderBadges();
    resetSimulation(false);
    updateRFPhysics();
  });

  chkAutoRatio.addEventListener('change', (e) => {
    state.autoJumpRatio = e.target.checked;
    if (state.autoJumpRatio) {
      state.jumpRatio = computeOptimalJumpRatio(state.numSides);
      jumpRatioSlider.value = state.jumpRatio.toFixed(3);
      jumpRatioVal.textContent = `${state.jumpRatio.toFixed(3)} [Auto]`;
      updateHeaderBadges();
      resetSimulation(false);
      updateRFPhysics();
    }
  });

  chkNoRepeatRule.addEventListener('change', (e) => {
    state.noRepeatRule = e.target.checked;
    resetSimulation(false);
  });

  speedSlider.addEventListener('input', (e) => {
    state.speed = parseInt(e.target.value, 10);
    speedVal.textContent = `${state.speed.toLocaleString()} pts / frame`;
  });

  pointSizeSlider.addEventListener('input', (e) => {
    state.pointSize = parseFloat(e.target.value);
    pointSizeVal.textContent = `${state.pointSize.toFixed(1)} px`;
    resetSimulation(false);
  });

  colorThemeSelect.addEventListener('change', (e) => {
    state.colorTheme = e.target.value;
    resetSimulation(false);
  });

  // Antenna Controls
  antennaPatchSelect.addEventListener('change', (e) => {
    state.numSides = parseInt(e.target.value, 10);
    numSidesSlider.value = state.numSides;
    numSidesVal.textContent = `N = ${state.numSides}`;
    initPolygonVertices();
    resetSimulation(false);
  });

  substrateSelect.addEventListener('change', (e) => {
    state.dielectricEr = parseFloat(e.target.value);
    updateRFPhysics();
  });

  patchSizeSlider.addEventListener('input', (e) => {
    state.patchSizeMm = parseInt(e.target.value, 10);
    patchSizeVal.textContent = `${state.patchSizeMm} mm`;
    updateRFPhysics();
  });

  antennaDepthSlider.addEventListener('input', (e) => {
    state.antennaDepth = parseInt(e.target.value, 10);
    state.recursionDepth = state.antennaDepth;
    antennaDepthVal.textContent = `Depth ${state.antennaDepth}`;
    updateRFPhysics();
  });

  // Action Buttons
  btnPlayPause.addEventListener('click', () => {
    state.isPaused = !state.isPaused;
    topStatus.textContent = state.isPaused ? 'PAUSED' : 'SIMULATING';
    topStatus.className = state.isPaused ? 'pill-value text-amber' : 'pill-value text-cyan';
    btnPlayPause.querySelector('span').textContent = state.isPaused ? 'Resume Simulation' : 'Pause Simulation';
  });

  btnResetSimulation.addEventListener('click', () => {
    resetSimulation(false);
  });

  btnResetGeometry.addEventListener('click', () => {
    state.autoJumpRatio = true;
    chkAutoRatio.checked = true;
    initPolygonVertices();
    resetSimulation(false);
  });

  // Segmented Mode Buttons
  document.querySelectorAll('.seg-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.seg-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.mode = btn.dataset.mode;
      resetSimulation(false);
    });
  });

  // Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(btn.dataset.tab).classList.add('active');
    });
  });

  // Presentation Modal
  btnPresentationModal.addEventListener('click', () => {
    presentationModal.classList.add('open');
  });
  btnCloseModal.addEventListener('click', () => {
    presentationModal.classList.remove('open');
  });
  presentationModal.addEventListener('click', (e) => {
    if (e.target === presentationModal) presentationModal.classList.remove('open');
  });

  // Export Blueprint Snapshot
  btnExportSnapshot.addEventListener('click', () => {
    const link = document.createElement('a');
    link.download = `FractalWave_Antenna_N${state.numSides}_d${state.antennaDepth}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
  });

  // Resize handler
  window.addEventListener('resize', resizeCanvases);

  // Initial Boot
  resizeCanvases();
  updateRFPhysics();
  requestAnimationFrame(renderLoop);

})();
