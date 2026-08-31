"""Add mathematical formulas to Slide 3 to support the BLUE/Qpar statement."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

OUTPUT_DIR = '/Users/linp24/Downloads'
INPUT = os.path.join(OUTPUT_DIR, 'Quantative Stain Analytics_v3.pptx')
OUTPUT = os.path.join(OUTPUT_DIR, 'Quantative Stain Analytics_v4.pptx')

# --- Step 1: Render equations as images ---
equations = [
    {
        'label': 'eq_beer_lambert',
        'title': 'Beer-Lambert Transform:',
        'eq': r'$\mathbf{V}_{OD} = -\ln\!\left(\frac{\mathbf{I}_{RGB}}{\mathbf{I}_0}\right)$',
    },
    {
        'label': 'eq_linear_model',
        'title': 'Linear Stain Mixing Model:',
        'eq': r'$\mathbf{Y} = \mathbf{C}\,\mathbf{W} + \mathbf{E}$',
        'note': r'$\mathbf{Y}$: observed OD,  $\mathbf{W}$: stain vectors,  $\mathbf{C}$: concentrations,  $\mathbf{E}$: noise',
    },
    {
        'label': 'eq_blue',
        'title': 'BLUE (Gauss-Markov):',
        'eq': r'$\hat{\mathbf{C}} = \left(\mathbf{W}^T \mathbf{W}\right)^{-1} \mathbf{W}^T \mathbf{Y}$',
        'note': r'$Q_{par}$ minimization $\;\Rightarrow\;$ optimal $\mathbf{W}$ $\;\Rightarrow\;$ BLUE for $\hat{\mathbf{C}}$',
    },
]

eq_paths = []
for item in equations:
    fig, ax = plt.subplots(figsize=(4.5, 1.2))
    ax.axis('off')

    y = 0.85
    ax.text(0.02, y, item['title'], fontsize=11, fontweight='bold',
            va='top', ha='left', transform=ax.transAxes,
            fontfamily='sans-serif')
    y -= 0.35
    ax.text(0.06, y, item['eq'], fontsize=14, va='top', ha='left',
            transform=ax.transAxes)
    if 'note' in item:
        y -= 0.35
        ax.text(0.06, y, item['note'], fontsize=9, va='top', ha='left',
                transform=ax.transAxes, color='#555555')

    path = os.path.join(OUTPUT_DIR, f"{item['label']}.png")
    fig.savefig(path, dpi=200, bbox_inches='tight', transparent=True,
                pad_inches=0.05)
    plt.close(fig)
    eq_paths.append(path)
    print(f"Rendered: {path}")

# --- Step 2: Embed equation images on Slide 3 ---
prs = Presentation(INPUT)
slide3 = prs.slides[2]

# Shrink the existing left body text box to make room
for shape in slide3.shapes:
    if ';193;' in shape.name and shape.has_text_frame:
        # Reduce height to ~2.0" (from 3.9")
        shape.height = Inches(2.0)
        print(f"Resized body text to height={Emu(shape.height).inches:.1f}\"")

# Place equations below the body text, in the left column area
left_margin = Inches(0.6)
eq_top = Inches(3.5)
eq_width = Inches(4.2)
eq_height = Inches(0.55)
spacing = Inches(0.05)

for i, path in enumerate(eq_paths):
    top = eq_top + i * (eq_height + spacing)
    pic = slide3.shapes.add_picture(path, left_margin, int(top), eq_width)
    print(f"Added {equations[i]['label']} at top={Emu(int(top)).inches:.2f}\"")

# --- Save ---
prs.save(OUTPUT)
print(f"\nSaved: {OUTPUT}")

# Clean up equation images
for p in eq_paths:
    os.remove(p)
    print(f"Cleaned: {p}")
