"""Add a new Slide 4: Mathematical Foundation, after Slide 3."""
from pptx import Presentation
from pptx.util import Inches, Emu
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

OUTPUT_DIR = '/Users/linp24/Downloads'
INPUT = os.path.join(OUTPUT_DIR, 'Quantative Stain Analytics_v3.pptx')
OUTPUT = os.path.join(OUTPUT_DIR, 'Quantative Stain Analytics_v4.pptx')

# --- Step 1: Render a single combined equation image ---
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.axis('off')

lines = [
    (0.02, 0.92, r'\textbf{1. Beer-Lambert Transform (RGB $\rightarrow$ Optical Density):}', 12, 'black'),
    (0.06, 0.82, r'$\mathbf{V}_{OD} = -\ln\!\left(\dfrac{\mathbf{I}_{RGB}}{\mathbf{I}_0}\right)$', 16, 'black'),

    (0.02, 0.68, r'\textbf{2. Linear Stain Mixing Model in OD Space:}', 12, 'black'),
    (0.06, 0.58, r'$\mathbf{Y} = \mathbf{C}\,\mathbf{W} + \boldsymbol{\varepsilon}$', 16, 'black'),
    (0.06, 0.47, r'$\mathbf{Y}$: observed OD    $\mathbf{W}$: stain vectors    $\mathbf{C}$: concentrations    $\boldsymbol{\varepsilon}$: noise', 10, '#444444'),

    (0.02, 0.34, r'\textbf{3. BLUE via Gauss-Markov Theorem:}', 12, 'black'),
    (0.06, 0.17, r'$\hat{\mathbf{C}} = \left(\mathbf{W}^T \mathbf{W}\right)^{-1} \mathbf{W}^T \mathbf{Y}$'
                 r'$\qquad \textrm{where } Q_{par} \textrm{ optimizes } \mathbf{W}$'
                 r'$\textrm{ to minimize } \mathrm{Var}(\hat{\mathbf{C}})$', 14, 'black'),

    (0.06, 0.04, r'$\mathbb{E}[\boldsymbol{\varepsilon}] = 0$, '
                 r'$\;\mathrm{Cov}(\boldsymbol{\varepsilon}) = \sigma^2 \mathbf{I}$'
                 r'$\;\;\Rightarrow\;\; \hat{\mathbf{C}}$ is BLUE', 11, '#333333'),
]

# Try LaTeX first, fall back to mathtext
try:
    plt.rcParams['text.usetex'] = True
    plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}\usepackage{amssymb}'
    for x, y, txt, size, color in lines:
        ax.text(x, y, txt, fontsize=size, va='top', ha='left',
                transform=ax.transAxes, color=color)
    eq_path = os.path.join(OUTPUT_DIR, 'math_slide.png')
    fig.savefig(eq_path, dpi=200, bbox_inches='tight', transparent=True, pad_inches=0.1)
except Exception:
    plt.close(fig)
    plt.rcParams['text.usetex'] = False
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.axis('off')
    lines_fallback = [
        (0.02, 0.92, 'Beer-Lambert Transform (RGB → Optical Density):', 12, 'black', 'bold'),
        (0.06, 0.82, r'$\mathbf{V}_{OD} = -\ln\left(\frac{\mathbf{I}_{RGB}}{\mathbf{I}_0}\right)$', 16, 'black', 'normal'),

        (0.02, 0.68, 'Linear Stain Mixing Model in OD Space:', 12, 'black', 'bold'),
        (0.06, 0.58, r'$\mathbf{Y} = \mathbf{C}\,\mathbf{W} + \varepsilon$', 16, 'black', 'normal'),
        (0.06, 0.48, r'$\mathbf{Y}$: observed OD    $\mathbf{W}$: stain vectors    $\mathbf{C}$: concentrations    $\varepsilon$: noise', 9, '#444444', 'normal'),

        (0.02, 0.35, 'BLUE via Gauss-Markov Theorem:', 12, 'black', 'bold'),
        (0.06, 0.22, r'$\hat{\mathbf{C}} = (\mathbf{W}^T\mathbf{W})^{-1}\mathbf{W}^T\mathbf{Y}$', 16, 'black', 'normal'),
        (0.06, 0.10, r'$Q_{par}$ optimizes $\mathbf{W}$ to minimize $Var(\hat{\mathbf{C}})$', 11, '#333333', 'normal'),
        (0.06, 0.01, r'$E[\varepsilon]=0$,  $Cov(\varepsilon)=\sigma^2 I$  $\Rightarrow$  $\hat{\mathbf{C}}$ is BLUE', 11, '#333333', 'normal'),
    ]
    for x, y, txt, size, color, weight in lines_fallback:
        ax.text(x, y, txt, fontsize=size, va='top', ha='left',
                transform=ax.transAxes, color=color, fontweight=weight)
    eq_path = os.path.join(OUTPUT_DIR, 'math_slide.png')
    fig.savefig(eq_path, dpi=200, bbox_inches='tight', transparent=True, pad_inches=0.1)

plt.close(fig)
print(f"Rendered: {eq_path}")

# --- Step 2: Create new slide 4 ---
prs = Presentation(INPUT)

# Use BLANK layout
blank_layout = None
for layout in prs.slide_layouts:
    if layout.name == 'BLANK':
        blank_layout = layout
        break

new_slide = prs.slides.add_slide(blank_layout)

# Move to position 3 (index 3, after slide 3)
slide_list = prs.slides._sldIdLst
ids = list(slide_list)
moved = ids[-1]
slide_list.remove(moved)
slide_list.insert(3, moved)

# Add title text box
from pptx.util import Pt
from pptx.dml.color import RGBColor

txBox = new_slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(8.1), Inches(0.5))
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
run = p.add_run()
run.text = "Mathematical Foundation"
run.font.size = Pt(24)
run.font.bold = True
run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

# Add subtitle
txBox2 = new_slide.shapes.add_textbox(Inches(0.6), Inches(0.9), Inches(8.1), Inches(0.4))
tf2 = txBox2.text_frame
p2 = tf2.paragraphs[0]
run2 = p2.add_run()
run2.text = "From Beer-Lambert Law to Optimal Stain Vector Estimation"
run2.font.size = Pt(14)
run2.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

# Add equation image
pic = new_slide.shapes.add_picture(eq_path, Inches(0.6), Inches(1.5), Inches(7.5))
print(f"Added equation image to new Slide 4")

# Add footer-style text
txBox3 = new_slide.shapes.add_textbox(Inches(0.6), Inches(4.7), Inches(8.0), Inches(0.3))
tf3 = txBox3.text_frame
p3 = tf3.paragraphs[0]
run3 = p3.add_run()
run3.text = "Under Gauss-Markov conditions, Qpar calibration converges to the variance-minimizing BLUE for stain vectors."
run3.font.size = Pt(10)
run3.font.italic = True
run3.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

# Save
prs.save(OUTPUT)
print(f"\nSaved: {OUTPUT}")

# Clean up
os.remove(eq_path)

# Verify
prs2 = Presentation(OUTPUT)
print(f"Total slides: {len(prs2.slides)}")
for i in range(5):
    s = prs2.slides[i]
    texts = []
    for sh in s.shapes:
        if sh.has_text_frame:
            t = sh.text_frame.text.strip()
            if t:
                texts.append(t[:80])
    print(f"  Slide {i+1}: {' | '.join(texts[:3])}")
