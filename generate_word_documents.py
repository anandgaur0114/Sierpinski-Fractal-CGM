import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_header_p(doc, text, level=1, space_before=14, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.bold = True
    if level == 1:
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(16, 44, 87) # Deep Navy
    elif level == 2:
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(30, 70, 120)
    else:
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(40, 40, 40)
    return p

def add_body_p(doc, text, bold_prefix="", italic_prefix="", space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.font.name = 'Times New Roman'
        r_b.font.size = Pt(11.5)
        r_b.bold = True

    if italic_prefix:
        r_i = p.add_run(italic_prefix)
        r_i.font.name = 'Times New Roman'
        r_i.font.size = Pt(11.5)
        r_i.italic = True

    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)
    return p

def add_bullet_p(doc, bold_title, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    r_b = p.add_run(bold_title)
    r_b.font.name = 'Times New Roman'
    r_b.font.size = Pt(11.5)
    r_b.bold = True

    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)
    return p

# ==============================================================================
# 1. BUILD PROJECT SYNOPSIS (.docx)
# ==============================================================================
def create_synopsis_docx():
    doc = Document()
    
    # Page setup: Normal 1 inch margins
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # ---------------- PAGE 1: COVER PAGE ----------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("A\nProject\nSYNOPSIS\nOf")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("REAL-TIME GENERALIZED N-GON AND SIERPINSKI FRACTAL GENERATOR USING CHAOS GAME ALGORITHM IN C++ & SFML")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(15)
    r.bold = True
    r.font.color.rgb = RGBColor(16, 44, 87)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("Submitted in partial fulfillment for the award of degree of\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.italic = True
    r2 = p.add_run("Bachelor of Technology\nDegree Of\nRajasthan Technical University, KOTA\n")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(13)
    r2.bold = True
    r3 = p.add_run("2026-2027")
    r3.font.name = 'Times New Roman'
    r3.font.size = Pt(12)
    r3.bold = True

    # 2-Column Table for Students and Guide
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_left = table.cell(0, 0)
    cell_right = table.cell(0, 1)

    p_l = cell_left.paragraphs[0]
    p_l.add_run("Submitted By:\n").bold = True
    p_l.add_run("Abhinav Bhatra (24EJCCA009)\nAmit kumar (24EJCCA027)\nAnand Gaur (24EJCCA030)\nAbhishek Sihag (24EJCCA012)")
    for run in p_l.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)

    p_r = cell_right.paragraphs[0]
    p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_r.add_run("ITS Coordinator (CC):\n").bold = True
    p_r.add_run("Ms. Mona Nagar\nAssistant Professor\nDept. of CSE (AI)")
    for run in p_r.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)

    # Department and College Footer
    p_foot = doc.add_paragraph()
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_foot.paragraph_format.space_before = Pt(30)
    r_dept = p_foot.add_run("DEPARTMENT OF\nCOMPUTER SCIENCE & ENGINEERING (ARTIFICIAL INTELLIGENCE)\nJAIPUR ENGINEERING COLLEGE AND RESEARCH CENTRE\n")
    r_dept.font.name = 'Times New Roman'
    r_dept.font.size = Pt(12)
    r_dept.bold = True
    r_addr = p_foot.add_run("Shri Ram ki Nangal, via Sitapura RIICO, Tonk Road, Sukhpuria, Bambala, Jaipur, Rajasthan - 302022")
    r_addr.font.name = 'Times New Roman'
    r_addr.font.size = Pt(10)

    doc.add_page_break()

    # ---------------- PAGE 2: ABSTRACT ----------------
    p_abs_title = doc.add_paragraph()
    p_abs_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs_title.paragraph_format.space_before = Pt(20)
    p_abs_title.paragraph_format.space_after = Pt(20)
    r = p_abs_title.add_run("ABSTRACT")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.bold = True
    r.underline = True

    add_body_p(doc, "Fractal geometry plays an indispensable role in contemporary Computer Graphics and Multimedia (CGM), offering rigorous mathematical formulations to simulate self-similar natural phenomena and procedural structures. The Sierpinski Triangle is an archetypal fractal displaying exact self-similarity, zero Lebesgue area, and infinite perimeter, characterized by a fractional Hausdorff dimension of D = log(3) / log(2) ~ 1.585.")
    add_body_p(doc, "This project presents a high-performance C++ desktop application developed with the Simple and Fast Multimedia Library (SFML 2.5+) to simulate and visualize fractal generation through two fundamental paradigms: the stochastic Chaos Game (Iterated Function Systems / random midpoint contraction) and deterministic Recursive Subdivision.")
    add_body_p(doc, "Furthermore, this work extends the classic 3-vertex Sierpinski triangle into an arbitrary N-sided regular polygon generator (N = 3 to 12)—commonly classified as Generalized N-Flakes (including the Sierpinski Carpet for N=4, Dürer's Pentagasket for N=5, and the Hexaflake for N=6). To prevent sub-shape overlap for higher-order polygons, the system dynamically calculates the mathematically optimal contraction ratio: r(N) = 1 / [2 * (1 + sum(cos(2*pi*k/N)))].")
    add_body_p(doc, "The rendering engine leverages hardware-accelerated persistent framebuffers (sf::RenderTexture), guaranteeing sustained 60 FPS performance even when accumulating over 500,000 vertices. The application incorporates extensive user input modalities, including real-time mouse dragging of polygon vertices for dynamic shape deformation, interactive click-to-seed starting point placement, on-screen graphical buttons, keyboard hotkeys, and an interactive terminal parameter prompt.")

    doc.add_page_break()

    # ---------------- PAGE 3: INTRODUCTION ----------------
    p_intro = doc.add_paragraph()
    p_intro.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_intro.paragraph_format.space_before = Pt(10)
    p_intro.paragraph_format.space_after = Pt(16)
    r = p_intro.add_run("INTRODUCTION")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.bold = True
    r.underline = True

    add_bullet_p(doc, "Problem Statement: ", "Traditional computer graphics curricula often introduce fractals through static equations, obscuring how deterministic geometric order emerges from stochastic random walks. Moreover, conventional lab programs restrict students to fixed triangles, omitting polygon generalization and suffering from severe GPU lag as plotted points exceed 100,000.")
    add_bullet_p(doc, "Scope of the Project: ", "Implementation of both Stochastic Chaos Game and Recursive Subdivision; generalization to regular N-gons (N=3 to 12) with mathematical jump ratios; real-time mouse vertex dragging for dynamic shape morphing; click-to-seed canvas input; and GPU texture caching sustaining 60 FPS at 500,000+ points.")
    add_bullet_p(doc, "Technologies Used: ", "C++14/C++17, SFML 2.5.1 (Simple and Fast Multimedia Library), Mersenne Twister Engine (std::mt19937), CMake, MinGW g++, and Git/GitHub.")
    add_bullet_p(doc, "Methodology: ", "Parametric circle coordinate generation for N-gon vertices; contractive affine transformations P_new = (1 - r)*P + r*V_chosen; 25 warmup iteration discards; and persistent off-screen framebuffer accumulation via sf::RenderTexture.")
    add_bullet_p(doc, "Expected Outcome: ", "An interactive desktop GUI that visually demonstrates order out of chaos, allowing users to alter polygon sides, drag vertices, adjust speeds, and change colors in real time without frame drops.")
    add_bullet_p(doc, "Applications of Project: ", "Procedural landscape and texture generation in video games, multiband fractal antenna design in telecommunications, fractal image compression, and educational tools for computer graphics.")

    doc.add_page_break()

    # ---------------- PAGE 4: CONCLUSIONS & FUTURE ENHANCEMENTS ----------------
    p_conc = doc.add_paragraph()
    p_conc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_conc.paragraph_format.space_before = Pt(10)
    p_conc.paragraph_format.space_after = Pt(16)
    r = p_conc.add_run("CONCLUSIONS AND FUTURE ENHANCEMENTS")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.bold = True
    r.underline = True

    add_header_p(doc, "Conclusions", level=2, space_before=4)
    add_body_p(doc, "The project successfully demonstrates that stochastic random midpoint iterations under contractive affine constraints strictly converge to the deterministic self-similar attractors predicted by Hutchinson's Theorem. By generalizing the system to regular N-gons with mathematically computed contraction ratios r(N) and off-screen persistent GPU caching, the application maintains high interactive frame rates (60 FPS) and provides a rich experimental platform for computer graphics education.")

    add_header_p(doc, "Future Enhancements", level=2, space_before=8)
    add_bullet_p(doc, "3D Fractal Extrusion: ", "Extending the 2D affine mapping engine to 3D Euclidean space to generate interactive 3D Sierpinski Tetrahedra and Menger Sponges using OpenGL shaders.")
    add_bullet_p(doc, "Compute Shader Parallelism: ", "Offloading random point generation from CPU to GPU compute shaders (GLSL/HLSL) to simulate 10 million points per second.")
    add_bullet_p(doc, "Audio-Reactive Visualization: ", "Connecting audio FFT frequency bands to polygon vertex deformation and palette transitions for live multimedia installations.")

    add_header_p(doc, "System Visual Outputs", level=2, space_before=10)
    
    img1_path = "screenshots/sierpinski_triangle_n3.png"
    img2_path = "screenshots/sierpinski_carpet_n4.png"
    
    if os.path.exists(img1_path) and os.path.exists(img2_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_img1 = p_img.add_run()
        run_img1.add_picture(img1_path, width=Inches(3.0))
        run_img1.add_text("   ")
        run_img2 = p_img.add_run()
        run_img2.add_picture(img2_path, width=Inches(3.0))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_c = p_cap.add_run("Figure: Real-time application outputs. Left: Sierpinski Triangle (N=3, r=0.500). Right: Sierpinski Carpet (N=4, r=0.500) with non-adjacent rule.")
        r_c.font.name = 'Times New Roman'
        r_c.font.size = Pt(9.5)
        r_c.italic = True

    doc.add_page_break()

    # ---------------- PAGE 5: REFERENCES ----------------
    p_ref = doc.add_paragraph()
    p_ref.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ref.paragraph_format.space_before = Pt(20)
    p_ref.paragraph_format.space_after = Pt(20)
    r = p_ref.add_run("References")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.bold = True
    r.font.color.rgb = RGBColor(16, 44, 87)

    refs = [
        "Mandelbrot, B. B. (1982). The Fractal Geometry of Nature. W. H. Freeman and Company, New York.",
        "Sierpinski, W. (1915). Sur une nouvelle courbe continue qui remplit toute une aire plane. Bulletin International de l'Academie des Sciences de Cracovie, Serie A, 577-578.",
        "Barnsley, M. F. (1988). Fractals Everywhere. Academic Press, Boston.",
        "Hutchinson, J. E. (1981). Fractals and self similarity. Indiana University Mathematics Journal, 30(5), 713-747.",
        "Elton, J. H. (1987). An ergodic theorem for iterated function systems. Ergodic Theory and Dynamical Systems, 7(4), 481-488.",
        "Hearn, D., & Baker, M. P. (2004). Computer Graphics with OpenGL (3rd ed.). Pearson Prentice Hall.",
        "SFML Team. (2022). Simple and Fast Multimedia Library Documentation (Version 2.5.1). Available: https://www.sfml-dev.org/documentation/2.5.1/",
        "Devaney, R. L. (1990). Chaos, Fractals, and Dynamics: Computer Experiments in Mathematics. Addison-Wesley."
    ]
    for i, ref in enumerate(refs, 1):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_num = p.add_run(f"[{i}] ")
        r_num.font.name = 'Times New Roman'
        r_num.font.size = Pt(11)
        r_num.bold = True
        r_t = p.add_run(ref)
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(11)

    doc.save("PROJECT_SYNOPSIS.docx")
    print("[SUCCESS] Generated PROJECT_SYNOPSIS.docx")

# ==============================================================================
# 2. BUILD PROJECT REPORT (.docx)
# ==============================================================================
def create_report_docx():
    doc = Document()
    
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # ---------------- COVER PAGE ----------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(15)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("A\nProject Report\nOn")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(14)
    r = p.add_run("REAL-TIME GENERALIZED N-GON AND SIERPINSKI FRACTAL GENERATOR USING CHAOS GAME AND ITERATED FUNCTION SYSTEMS IN C++ & SFML")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(15)
    r.bold = True
    r.font.color.rgb = RGBColor(16, 44, 87)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("Submitted in partial fulfillment for the award of degree of\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.italic = True
    r2 = p.add_run("Bachelor of Technology\nDegree Of\nRajasthan Technical University, KOTA\n")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(13)
    r2.bold = True
    r3 = p.add_run("2026-2027\n")
    r3.font.name = 'Times New Roman'
    r3.font.size = Pt(12)
    r3.bold = True

    # Submitted by Table
    t = doc.add_table(rows=1, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_l = t.cell(0, 0)
    c_r = t.cell(0, 1)

    p_l = c_l.paragraphs[0]
    p_l.add_run("Submitted By:\n").bold = True
    p_l.add_run("Abhinav Bhatra (24EJCCA009)\nAmit kumar (24EJCCA027)\nAnand Gaur (24EJCCA030)\nAbhishek Sihag (24EJCCA012)")
    for run in p_l.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)

    p_r = c_r.paragraphs[0]
    p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_r.add_run("ITS Coordinator (CC):\n").bold = True
    p_r.add_run("Ms. Mona Nagar\nAssistant Professor\nDept. of CSE (AI)")
    for run in p_r.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)

    p_foot = doc.add_paragraph()
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_foot.paragraph_format.space_before = Pt(35)
    r_dept = p_foot.add_run("DEPARTMENT OF\nCOMPUTER SCIENCE & ENGINEERING (ARTIFICIAL INTELLIGENCE)\nJAIPUR ENGINEERING COLLEGE AND RESEARCH CENTRE\n")
    r_dept.font.name = 'Times New Roman'
    r_dept.font.size = Pt(12)
    r_dept.bold = True
    r_addr = p_foot.add_run("Shri Ram ki Nangal, via Sitapura RIICO, Tonk Road, Sukhpuria, Bambala, Jaipur, Rajasthan - 302022")
    r_addr.font.name = 'Times New Roman'
    r_addr.font.size = Pt(10)

    doc.add_page_break()

    # ---------------- TABLE OF CONTENTS ----------------
    p_toc = doc.add_paragraph()
    p_toc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc.paragraph_format.space_before = Pt(10)
    p_toc.paragraph_format.space_after = Pt(15)
    r = p_toc.add_run("TABLE OF CONTENTS")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.bold = True
    r.underline = True

    toc_items = [
        ("Introduction", "1"),
        ("Objective", "5"),
        ("Methodology And Planning", "6"),
        ("Literature Review", "13"),
        ("Applications of the Project", "16"),
        ("Block Diagram", "18"),
        ("UML Diagram", "20"),
        ("Screenshots", "23"),
        ("References", "29"),
        ("Approval of the Project", "30")
    ]

    toc_table = doc.add_table(rows=len(toc_items) + 1, cols=2)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Header row
    hdr_c0 = toc_table.cell(0, 0)
    hdr_c1 = toc_table.cell(0, 1)
    hdr_c0.paragraphs[0].add_run("Chapter / Section Title").bold = True
    hdr_c1.paragraphs[0].add_run("Page No.").bold = True
    hdr_c1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_cell_background(hdr_c0, "EAECEF")
    set_cell_background(hdr_c1, "EAECEF")

    for i, (title, page) in enumerate(toc_items, 1):
        c0 = toc_table.cell(i, 0)
        c1 = toc_table.cell(i, 1)
        c0.paragraphs[0].add_run(title)
        c1.paragraphs[0].add_run(page)
        c1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)

    doc.add_page_break()

    # ---------------- 1. INTRODUCTION ----------------
    add_header_p(doc, "1. Introduction", level=1)
    add_body_p(doc, "Euclidean geometry deals with smooth, integer-dimensional entities such as lines (1D), circles and polygons (2D), and spheres and polyhedra (3D). However, nature exhibits intricate geometric shapes that display infinite irregularity and fine detail regardless of the magnification scale—including coastlines, lightning paths, blood vessels, mountain ridges, and cloud formations. In 1975, Benoit Mandelbrot established the field of Fractal Geometry to describe objects that exhibit self-similarity and possess non-integer Hausdorff dimensions.")
    
    add_header_p(doc, "1.1 The Sierpinski Gasket / Triangle", level=2)
    add_body_p(doc, "First described by Polish mathematician Wacław Sierpiński in 1915, the Sierpinski Triangle (or Sierpinski Gasket) is an archetypal fractal. It is traditionally constructed deterministically by starting with an equilateral triangle, connecting the midpoints of its three sides to form an inverted central triangle, excising that central triangle, and recursively repeating the excision infinitely on the three remaining sub-triangles.")

    add_header_p(doc, "1.2 Mathematical Derivation of Hausdorff Dimension", level=2)
    add_body_p(doc, "In Euclidean geometry, when an object with dimension D is scaled down by a linear scaling factor s, it divides into N self-similar pieces according to the relation: N = (1/s)^D.")
    add_body_p(doc, "Taking natural logarithms on both sides: ln(N) = D * ln(1/s). Therefore: D = ln(N) / ln(1/s).")
    add_body_p(doc, "For the Sierpinski Triangle, each iteration subdivides the shape into N = 3 identical copies, each scaled by s = 1/2 = 0.5. Substituting into the formula:")
    add_body_p(doc, "D = ln(3) / ln(1 / 0.5) = ln(3) / ln(2) ~ 1.098612 / 0.693147 ~ 1.5849625...")
    add_body_p(doc, "Because 1 < 1.585 < 2, the Sierpinski Triangle has greater complexity and boundary detail than a 1D line, but is too sparse to occupy a 2D Euclidean surface area.")

    add_header_p(doc, "1.3 The Area and Perimeter Paradox", level=2)
    add_body_p(doc, "Let the initial solid equilateral triangle have area A_0 and perimeter P_0. At step k, exactly 1/4 of the remaining area is excised:")
    add_body_p(doc, "A_k = A_0 * (3/4)^k  -->  lim_{k -> infinity} A_k = 0  (Area converges to zero).")
    add_body_p(doc, "Conversely, each step exposes new internal edges, multiplying perimeter by 3/2:")
    add_body_p(doc, "P_k = P_0 * (3/2)^k  -->  lim_{k -> infinity} P_k = infinity  (Perimeter tends to infinity).")
    add_body_p(doc, "This mathematical paradox—a shape possessing zero surface area enclosed by an infinite perimeter—is a hallmark of fractal geometry.")

    doc.add_page_break()

    # ---------------- 2. OBJECTIVE ----------------
    add_header_p(doc, "2. Objective", level=1)
    add_body_p(doc, "The primary objective of this project is to bridge theoretical fractal mathematics and real-time computer graphics by developing an interactive, GPU-accelerated C++ application using SFML 2.5+.")
    add_bullet_p(doc, "Stochastic Chaos Game Simulation: ", "Implement the random midpoint contraction algorithm to demonstrate how deterministic self-similar fractals emerge from pseudo-random point walks.")
    add_bullet_p(doc, "Deterministic Subdivision Comparison: ", "Implement the classic recursive triangle-splitting method (depths 0 to 8) to compare top-down hierarchical tessellation with bottom-up stochastic iteration.")
    add_bullet_p(doc, "Generalization to Arbitrary N-Gons: ", "Expand the attractor boundary from an equilateral triangle (N=3) to regular polygons up to N=12 (N-Flakes), computing mathematically exact contraction ratios r(N).")
    add_bullet_p(doc, "Stable 60 FPS Performance: ", "Use persistent off-screen framebuffers (sf::RenderTexture) to render over 500,000 points without frame drops.")
    add_bullet_p(doc, "Multi-Modal Interactive User Input: ", "Empower users to drag polygon vertices in real time using the mouse, click to set custom starting seed points, click on-screen GUI buttons, use keyboard shortcuts, or input parameters via terminal prompt.")

    # ---------------- 3. METHODOLOGY AND PLANNING ----------------
    add_header_p(doc, "3. Methodology And Planning", level=1)
    add_header_p(doc, "3.1 Algorithm 1: The Chaos Game", level=2)
    add_body_p(doc, "The Chaos Game operates iteratively: 1) Initialize N polygon vertices V_0 ... V_{N-1}. 2) Choose an arbitrary starting point P_0. 3) Discard the first 25 warmup iterations. 4) In each frame, select a random vertex V_i with probability 1/N. 5) Compute the contracted position P_{k+1} = (1 - r)*P_k + r*V_i. 6) Draw the new point to the persistent buffer.")

    add_header_p(doc, "3.2 Iterated Function Systems & Hutchinson Operator", level=2)
    add_body_p(doc, "An Iterated Function System (IFS) consists of contractive affine mappings {f_1, ..., f_N}. By the Banach Fixed-Point Theorem and Hutchinson's Theorem (1981), there exists a unique compact attractor A satisfying A = Union_{i=1}^N f_i(A). Elton's Ergodic Theorem guarantees that the random orbit generated by the Chaos Game is dense in A with probability 1.")

    add_header_p(doc, "3.3 Generalization to Regular N-Gons & Contraction Ratio r(N)", level=2)
    add_body_p(doc, "For an arbitrary regular N-gon, vertices are placed parametrically: V_k = (cx + R*cos(theta_k), cy + R*sin(theta_k)), with theta_k = -pi/2 + 2*pi*k/N. To ensure sub-polygons touch without overlapping, the contraction ratio r(N) is derived:")
    add_body_p(doc, "r(N) = 1 / [ 2 * ( 1 + sum_{k=1}^{floor(N/4)} cos(2*pi*k / N) ) ]")
    add_body_p(doc, "For N=3: r = 0.500 (Sierpinski Gasket). For N=4: r = 0.500 (Sierpinski Carpet under non-adjacent rule). For N=5: r = (3 - sqrt(5))/2 ~ 0.382 (Dürer's Pentagasket / Golden Ratio). For N=6: r = 1/3 ~ 0.333 (Hexaflake). For N=8: r = 1/(2 + sqrt(2)) ~ 0.293 (Octaflake).")

    add_header_p(doc, "3.4 Team Work Distribution", level=2)
    team_table = doc.add_table(rows=5, cols=3)
    team_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Member Name", "Roll No.", "Project Responsibilities"]
    for j, h in enumerate(headers):
        cell = team_table.cell(0, j)
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "EAECEF")
    
    t_data = [
        ("Anand Gaur", "24EJCCA030", "Mathematical derivation of r(N), GPU texture caching, Git repo setup."),
        ("Abhinav Bhatra", "24EJCCA009", "Chaos Game engine, Mersenne Twister RNG, and warmup discard logic."),
        ("Amit kumar", "24EJCCA027", "Recursive subdivision, solid/wireframe mesh generation, depth handling."),
        ("Abhishek Sihag", "24EJCCA012", "Mouse vertex dragging, click-to-seed, HUD controls, documentation.")
    ]
    for i, row in enumerate(t_data, 1):
        for j, val in enumerate(row):
            cell = team_table.cell(i, j)
            cell.paragraphs[0].add_run(val)
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)

    doc.add_page_break()

    # ---------------- 4. LITERATURE REVIEW ----------------
    add_header_p(doc, "4. Literature Review", level=1)
    add_body_p(doc, "The mathematical foundation of fractals dates back to Wacław Sierpiński (1915) and Felix Hausdorff (1918). Benoit Mandelbrot's seminal 1982 work 'The Fractal Geometry of Nature' unified these concepts and demonstrated that complex natural phenomena obey scale-invariant fractal laws rather than Euclidean geometry.")
    add_body_p(doc, "John Hutchinson (1981) placed fractals on a rigorous analytical foundation by formulating Iterated Function Systems on complete metric spaces. Michael Barnsley (1988) popularized the Chaos Game in 'Fractals Everywhere', proving that stochastic iterations faithfully trace deterministic attractors.")
    add_body_p(doc, "In modern computer graphics, SFML provides an optimal balance between low-level OpenGL GPU acceleration and clean C++ object-oriented architecture, enabling hardware-buffered texture caching for massive point clouds.")

    # ---------------- 5. APPLICATIONS OF THE PROJECT ----------------
    add_header_p(doc, "5. Applications of the Project", level=1)
    add_bullet_p(doc, "Procedural Modeling in Game Engines: ", "Procedural generation of terrain, mountains, foliage, and textures in game engines like Unreal Engine and Unity.")
    add_bullet_p(doc, "Fractal Antenna Engineering: ", "Design of compact multiband cellular and satellite antennas utilizing self-similar Sierpinski geometries.")
    add_bullet_p(doc, "Fractal Image Compression: ", "Compressing images by encoding local self-similar domain-to-range contractive affine maps.")
    add_bullet_p(doc, "AI & Computer Vision: ", "Using fractal dimensions as texture feature descriptors for biomedical image analysis (e.g. tumor boundary detection).")

    # ---------------- 6. BLOCK DIAGRAM ----------------
    add_header_p(doc, "6. Block Diagram", level=1)
    add_body_p(doc, "The software architecture comprises four distinct interacting subsystems:")
    add_bullet_p(doc, "1. User Input Layer: ", "Captures mouse drag coordinates, canvas click seeds, on-screen GUI buttons, keyboard hotkeys, and console input.")
    add_bullet_p(doc, "2. Mathematics & Geometry Engine: ", "Computes parametric polygon vertices, calculates optimal jump ratio r(N), executes random contraction mappings, and manages recursive tessellation.")
    add_bullet_p(doc, "3. SFML Render Pipeline: ", "Batches new points into sf::VertexArray and draws incrementally to a persistent off-screen sf::RenderTexture.")
    add_bullet_p(doc, "4. Presentation Layer: ", "Blits cached texture sprite, draws vertex halo handles, renders HUD sidebar, and displays at 60 FPS.")

    doc.add_page_break()

    # ---------------- 7. UML DIAGRAM ----------------
    add_header_p(doc, "7. UML Diagram", level=1)
    add_header_p(doc, "7.1 Class Structure", level=2)
    add_body_p(doc, "The system architecture is organized into modular classes and structures:")
    add_bullet_p(doc, "FractalConfig: ", "Encapsulates global simulation parameters (numSides, jumpRatio, targetPoints, pointsPerFrame, pointSize, recursionDepth, wireframeMode).")
    add_bullet_p(doc, "GUIButton: ", "Stores bounding rectangles, action IDs, and dynamic labels for clickable HUD buttons.")
    add_bullet_p(doc, "FractalEngine: ", "Contains core mathematical algorithms: initPolygon(), chaosGameStep(), generateRecursive(), and computeOptimalJumpRatio().")
    add_bullet_p(doc, "InputManager: ", "Processes SFML events, detects vertex hover and dragging, handles button clicks, and prompts terminal input.")

    add_header_p(doc, "7.2 Execution Sequence", level=2)
    add_body_p(doc, "In each frame cycle: 1) sf::Event polling handles user mouse/keyboard input. 2) If vertex is dragged, polygon coordinates update. 3) chaosGameStep() executes M contraction iterations. 4) Points are blitted to sf::RenderTexture. 5) Main window draws the persistent canvas sprite, vertex handles, and HUD panel.")

    # ---------------- 8. SCREENSHOTS ----------------
    add_header_p(doc, "8. Screenshots & Visual Outputs", level=1)
    add_body_p(doc, "The application was compiled and tested on Windows 10/11 using MinGW GCC and SFML 2.5.1. Below are authentic visual outputs captured from the running software:")

    img1_path = "screenshots/sierpinski_triangle_n3.png"
    img2_path = "screenshots/sierpinski_carpet_n4.png"

    if os.path.exists(img1_path):
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.add_run().add_picture(img1_path, width=Inches(5.6))
        p_cap1 = doc.add_paragraph()
        p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_c1 = p_cap1.add_run("Figure 8.1: Real-Time Sierpinski Triangle (N=3, r=0.500) generated with 100,000 points and IFS 3-Vertex Color Palette at 58.8 FPS.")
        r_c1.font.name = 'Times New Roman'
        r_c1.font.size = Pt(10)
        r_c1.italic = True

    if os.path.exists(img2_path):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.add_run().add_picture(img2_path, width=Inches(5.6))
        p_cap2 = doc.add_paragraph()
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_c2 = p_cap2.add_run("Figure 8.2: Real-Time Sierpinski Carpet (N=4, r=0.500) generated under Non-Adjacent Vertex Restriction Rule at 59.2 FPS.")
        r_c2.font.name = 'Times New Roman'
        r_c2.font.size = Pt(10)
        r_c2.italic = True

    doc.add_page_break()

    # ---------------- 9. REFERENCES ----------------
    add_header_p(doc, "9. References", level=1)
    refs = [
        "Mandelbrot, B. B. (1982). The Fractal Geometry of Nature. W. H. Freeman and Company, New York.",
        "Sierpinski, W. (1915). Sur une nouvelle courbe continue qui remplit toute une aire plane. Bulletin International de l'Academie des Sciences de Cracovie, Serie A, 577-578.",
        "Barnsley, M. F. (1988). Fractals Everywhere. Academic Press, Boston.",
        "Hutchinson, J. E. (1981). Fractals and self similarity. Indiana University Mathematics Journal, 30(5), 713-747.",
        "Elton, J. H. (1987). An ergodic theorem for iterated function systems. Ergodic Theory and Dynamical Systems, 7(4), 481-488.",
        "Hearn, D., & Baker, M. P. (2004). Computer Graphics with OpenGL (3rd ed.). Pearson Prentice Hall.",
        "SFML Team. (2022). Simple and Fast Multimedia Library Documentation (Version 2.5.1). Available: https://www.sfml-dev.org/documentation/2.5.1/",
        "Devaney, R. L. (1990). Chaos, Fractals, and Dynamics: Computer Experiments in Mathematics. Addison-Wesley.",
        "Foley, J. D., van Dam, A., Feiner, S. K., & Hughes, J. F. (1996). Computer Graphics: Principles and Practice in C (2nd ed.). Addison-Wesley Professional."
    ]
    for i, ref in enumerate(refs, 1):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_num = p.add_run(f"[{i}] ")
        r_num.font.name = 'Times New Roman'
        r_num.font.size = Pt(11)
        r_num.bold = True
        r_t = p.add_run(ref)
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(11)

    # ---------------- 10. APPROVAL OF THE PROJECT ----------------
    doc.add_page_break()
    p_app = doc.add_paragraph()
    p_app.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_app.paragraph_format.space_before = Pt(15)
    p_app.paragraph_format.space_after = Pt(15)
    r = p_app.add_run("10. APPROVAL OF THE PROJECT")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.bold = True
    r.underline = True

    p_c_head = doc.add_paragraph()
    p_c_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p_c_head.add_run("JAIPUR ENGINEERING COLLEGE AND RESEARCH CENTRE\nDEPARTMENT OF COMPUTER SCIENCE & ENGINEERING (ARTIFICIAL INTELLIGENCE)\n\n")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(12)
    r1.bold = True
    r2 = p_c_head.add_run("CERTIFICATE OF APPROVAL\n")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(14)
    r2.bold = True
    r2.underline = True

    add_body_p(doc, "This is to certify that the project report entitled 'REAL-TIME GENERALIZED N-GON AND SIERPINSKI FRACTAL GENERATOR USING CHAOS GAME AND ITERATED FUNCTION SYSTEMS IN C++ & SFML' submitted by:")
    add_body_p(doc, "  • Abhinav Bhatra (Roll No: 24EJCCA009)\n  • Amit kumar (Roll No: 24EJCCA027)\n  • Anand Gaur (Roll No: 24EJCCA030)\n  • Abhishek Sihag (Roll No: 24EJCCA012)")
    add_body_p(doc, "in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Science & Engineering (Artificial Intelligence) of Rajasthan Technical University, Kota, is an authentic record of the work carried out by them under my guidance and supervision.")
    add_body_p(doc, "To the best of my knowledge, the matter embodied in this project report has not been submitted to any other university or institute for the award of any degree or diploma.\n\n\n")

    # Signatures
    t_sig = doc.add_table(rows=2, cols=2)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    cell_s1 = t_sig.cell(0, 0)
    cell_s2 = t_sig.cell(0, 1)
    
    p_s1 = cell_s1.paragraphs[0]
    p_s1.add_run("_____________________________\nMs. Mona Nagar\nProject Coordinator (CC) / Assistant Professor\nDepartment of CSE (AI), JECRC").font.name = 'Times New Roman'
    
    p_s2 = cell_s2.paragraphs[0]
    p_s2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_s2.add_run("_____________________________\nHead of Department\nDepartment of CSE (AI)\nJECRC, Jaipur").font.name = 'Times New Roman'

    p_ext = doc.add_paragraph()
    p_ext.paragraph_format.space_before = Pt(40)
    p_ext.add_run("_____________________________\nExternal Examiner\nDate: ________________________").font.name = 'Times New Roman'

    doc.save("PROJECT_REPORT.docx")
    print("[SUCCESS] Generated PROJECT_REPORT.docx")

if __name__ == "__main__":
    create_synopsis_docx()
    create_report_docx()
