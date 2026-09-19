# Computer Graphics & Multimedia (CGM) Lab: Sierpinski Triangle & Chaos Game
## Theory, Mathematical Derivations & Viva Guide for B.Tech CSE (AI)

---

### 1. Introduction & Overview
The **Sierpinski Triangle** (also called the *Sierpinski Gasket* or *Sierpinski Sieve*) was first described by Polish mathematician Wacław Sierpiński in 1915. It is one of the foundational examples in Fractal Geometry, demonstrating how simple recursive rules or stochastic iterations generate infinite detail, exact self-similarity, and a non-integer (fractional) dimension.

In Computer Graphics, the Sierpinski Triangle is standardly studied through two distinct generation paradigms:
1. **Deterministic Recursive Subdivision** (Top-down geometric splitting)
2. **Stochastic Iterated Function System (The Chaos Game)** (Bottom-up random walk)

---

### 2. Mathematical Foundation & Properties

#### A. Self-Similarity
A geometric set $S$ is strictly self-similar if it can be decomposed into $N$ non-overlapping copies of itself, each scaled down by a linear scaling factor $s < 1$:
$$S = \bigcup_{i=1}^N \phi_i(S)$$
For the Sierpinski Triangle:
- Number of self-similar copies: $N = 3$
- Scaling factor: $s = \frac{1}{2} = 0.5$

#### B. Derivation of the Hausdorff / Fractal Dimension
Euclidean shapes have integer dimensions:
- A line segment divided into $N=2$ pieces has scale $s = 1/2 \implies D = \frac{\log 2}{\log 2} = 1$.
- A square divided into $N=4$ pieces has scale $s = 1/2 \implies D = \frac{\log 4}{\log 2} = 2$.
- A cube divided into $N=8$ pieces has scale $s = 1/2 \implies D = \frac{\log 8}{\log 2} = 3$.

For any self-similar fractal:
$$N = \left(\frac{1}{s}\right)^D \implies \log(N) = D \cdot \log\left(\frac{1}{s}\right)$$

Solving for the Hausdorff dimension $D$:
$$D = \frac{\log(N)}{\log(1/s)} = \frac{\log(3)}{\log(2)} \approx \frac{1.098612}{0.693147} \approx 1.5849625\dots$$

**Physical Interpretation for Viva:**
The Sierpinski Triangle has a dimension strictly between 1 and 2 ($1 < 1.585 < 2$). It has far more intricate detail and perimeter than a 1-dimensional curve, yet it is too sparse and hollow to fill a 2-dimensional plane (its 2D Lebesgue measure/area is zero).

#### C. Limiting Area and Perimeter Paradox
Let the original solid equilateral triangle have side length $L_0$ and area $A_0 = \frac{\sqrt{3}}{4} L_0^2$.

At each recursive step $n$:
1. **Area**: At each step, $1/4$ of the area is excised (the central upside-down triangle), leaving $3/4$ of the remaining area.
   $$A_n = A_0 \left(\frac{3}{4}\right)^n$$
   As $n \to \infty$:
   $$\lim_{n \to \infty} A_n = A_0 \lim_{n \to \infty} \left(\frac{3}{4}\right)^n = 0$$
   *The area of the Sierpinski Gasket is exactly zero!*

2. **Perimeter**: At each step, 3 new inner edges are exposed, multiplying the total boundary length by $3/2$.
   $$P_n = P_0 \left(\frac{3}{2}\right)^n$$
   As $n \to \infty$:
   $$\lim_{n \to \infty} P_n = P_0 \lim_{n \to \infty} \left(\frac{3}{2}\right)^n = \infty$$
   *The perimeter of the Sierpinski Gasket is infinite!*

---

### 3. How the Chaos Game Works (Iterated Function Systems)

#### The Algorithm
1. Choose 3 fixed vertices $V_0, V_1, V_2$ of an equilateral triangle.
2. Select an arbitrary initial seed point $P_0 = (x_0, y_0)$ (anywhere on the screen or inside the triangle).
3. In each iteration $k = 1, 2, 3, \dots$:
   - Randomly choose one vertex $V_{chosen} \in \{V_0, V_1, V_2\}$ with equal probability $p = 1/3$.
   - Calculate the midpoint:
     $$P_k = \frac{P_{k-1} + V_{chosen}}{2}$$
   - Plot $P_k$ on the canvas (discarding the first 15–20 transient points).

#### Why Does a Purely Random Game Form an Ordered Fractal?
Students are almost always asked in viva: *"If the choice of vertex is completely random, why doesn't it fill the entire triangle uniformly with noise?"*

**The Mathematical Reason:**
The Chaos Game is a concrete realization of an **Iterated Function System (IFS)**.
Each vertex $V_i$ defines a contractive affine transformation $f_i: \mathbb{R}^2 \to \mathbb{R}^2$:
$$f_i(P) = \frac{1}{2}P + \frac{1}{2}V_i$$
Since the contraction factor is $r = 1/2 < 1$, each $f_i$ is a strict contraction mapping on the metric space of non-empty compact subsets under the Hausdorff metric.

By the **Banach Fixed-Point Theorem** and **Hutchinson's Theorem (1981)**, there exists a *unique* non-empty compact set $A$ (the attractor) such that:
$$A = f_0(A) \cup f_1(A) \cup f_2(A)$$
This attractor $A$ is precisely the Sierpinski Triangle.

According to **Elton's Ergodic Theorem (1987)**, when we apply randomly chosen transformations $f_i$ sequentially:
$$P_k = f_{\sigma_k}(f_{\sigma_{k-1}}(\dots f_{\sigma_1}(P_0)\dots))$$
the sequence of points $\{P_k\}_{k=0}^\infty$ is distributed densely and ergodically over the attractor $A$ with probability 1.

#### Why Do Points Never Land in the Central Triangle?
1. The coordinates of any point inside the central inverted triangle cannot be written as the midpoint between a point on the attractor and any corner vertex.
2. If the initial starting point $P_0$ happens to be inside a "hole" or outside the triangle, each step cuts its distance to the true attractor in half:
   $$\text{dist}(P_k, A) \le \left(\frac{1}{2}\right)^k \text{dist}(P_0, A)$$
   After just 20 iterations, $(1/2)^{20} \approx 9.5 \times 10^{-7}$, which is sub-pixel level on any display. Thus, the orbit is permanently trapped inside the fractal attractor!

---

### 4. Comparison of Methods

| Feature | Chaos Game (Random Midpoints) | Recursive Subdivision |
| :--- | :--- | :--- |
| **Approach** | Stochastic (Iterative / Bottom-Up) | Deterministic (Hierarchical / Top-Down) |
| **Data Primitive** | Individual Points/Pixels (`sf::Points`) | Triangles/Polygons (`sf::Triangles`) |
| **Rendering Process** | Real-time point accumulation over time | Instantaneous geometric mesh generation |
| **Time Complexity** | $O(N)$ for $N$ plotted points | $O(3^d)$ for recursion depth $d$ |
| **Memory Footprint** | $O(1)$ dynamic memory using `sf::RenderTexture` | $O(3^d)$ vertices stored in vertex buffer |
| **Interactive Feature** | Continuous animation, point density slider | Depth slider (0 to 8), Wireframe/Solid toggle |

---

### 5. CGM Lab Viva Questions & Model Answers

**Q1: What is an Iterated Function System (IFS)?**
> **Answer:** An Iterated Function System is a finite set of contractive affine mappings $\{f_1, f_2, \dots, f_m\}$ acting on a complete metric space. By Banach's Fixed Point Theorem, every IFS has a unique invariant compact set called the **attractor** $A$, satisfying $A = \bigcup_{i=1}^m f_i(A)$. The Sierpinski triangle is generated by 3 contractions, each scaling by $1/2$ toward a vertex.

**Q2: How do you calculate the Hausdorff dimension of the Sierpinski triangle?**
> **Answer:** Using the self-similarity relation $N = (1/s)^D$, where $N$ is the number of self-similar pieces ($N=3$) and $s$ is the scaling factor ($s=1/2$). Taking natural logarithms: $D = \frac{\ln(3)}{\ln(1/0.5)} = \frac{\ln(3)}{\ln(2)} \approx 1.585$.

**Q3: Why do we discard the first 15–20 points in the Chaos Game?**
> **Answer:** The initial seed point $P_0$ is chosen arbitrarily and may not lie on the fractal attractor. Because each iteration contracts the distance to the attractor by $1/2$, the first few points represent a transient phase. Discarding them prevents spurious isolated pixels from appearing outside the fractal.

**Q4: What is the area and perimeter of the Sierpinski triangle in the limit?**
> **Answer:** At each subdivision step, $1/4$ of the remaining area is removed, so $A_n = A_0 (3/4)^n \to 0$ as $n \to \infty$. Conversely, the perimeter grows by a factor of $3/2$ per step, so $P_n = P_0 (3/2)^n \to \infty$. It has zero area and infinite perimeter.

**Q5: How does the SFML implementation maintain 60 FPS while plotting 100,000+ points?**
> **Answer:** Instead of re-drawing all 100,000 individual shapes every frame, the program renders new points incrementally to an off-screen `sf::RenderTexture` (persistent framebuffer). Each frame, the main loop simply draws this cached texture to the window in a single GPU draw call.

**Q6: What happens if the jump factor is changed from 1/2 to something else?**
> **Answer:**
> - If jump factor $< 1/2$ (e.g. $1/3$): The sub-triangles do not touch, creating a Cantor dust-like detached fractal.
> - If jump factor $= 1/2$: The standard Sierpinski gasket forms.
> - If jump factor $> 1/2$ (e.g. $2/3$): The triangles overlap, producing a solid filled triangle with higher density regions.
