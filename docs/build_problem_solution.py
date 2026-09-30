"""Build docs/AmropaliNet_Problem_Solution.pdf - problem statement + solution (environment focus).

Run:  python docs/build_problem_solution.py
Needs fpdf2 (already in the project requirements). Uses the bundled Hind Siliguri font.
"""
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "mango_disease_ai" / "fonts"
OUT = ROOT / "docs" / "AmropaliNet_Problem_Solution.pdf"

GREEN = (46, 125, 50)
DARK = (29, 58, 31)
SOFT = (84, 104, 86)
MANGO = (239, 138, 0)
TINT = (241, 247, 234)
LINE = (214, 228, 205)
RED = (190, 55, 45)
RED_TINT = (252, 236, 233)

# Official UN SDG colours
SDG = {
    1: ("No Poverty", (229, 36, 59)),
    2: ("Zero Hunger", (221, 166, 58)),
    3: ("Good Health", (76, 159, 56)),
    6: ("Clean Water", (38, 189, 226)),
    12: ("Responsible Production", (191, 139, 46)),
    13: ("Climate Action", (63, 126, 68)),
    15: ("Life on Land", (86, 192, 43)),
}

# ---------------------------------------------------------------- text
PROBLEM = [
    "Amrapali is Bangladesh's favourite everyday mango and the main source of income for thousands of "
    "farming families in Rajshahi, Chapainawabganj, Naogaon and the hill districts. Every season it is attacked "
    "by six common diseases: anthracnose, bacterial canker, powdery mildew, scab, sooty mould and stem-end rot.",
    "Most farmers cannot tell these diseases apart, and an agricultural officer is rarely at hand when the first "
    "spots appear. The usual answer is blanket, calendar spraying: the whole orchard is sprayed with several "
    "fungicides and insecticides \"just in case\", again and again from flowering to harvest.",
    "This turns a farming problem into an environmental one. Surplus chemicals wash into soil, ponds and "
    "groundwater, harming aquatic life and village drinking water (SDG 6). Spraying at flowering kills the bees "
    "and other pollinators that mango trees need to set fruit, and repeated doses breed resistant pathogens "
    "(SDG 15). Farm workers and their families breathe and handle these chemicals, often without protection (SDG 3).",
    "The second problem is waste. When disease is noticed late, it has already spread, and infected fruit rots on "
    "the tree, in storage or in transport. Every discarded mango wastes the water, land, fertiliser, fuel and "
    "labour used to grow it, and rotting fruit releases greenhouse gases (SDG 12, SDG 13). Lost harvests and "
    "wasted chemical costs push small farmers towards poverty and shrink the local food supply (SDG 1, SDG 2).",
    "The root cause is one missing piece of knowledge at the right moment: which disease is this, and what is the "
    "smallest treatment that works? Without it, farmers overspray, lose fruit and damage the ecosystem their "
    "orchards depend on - season after season.",
]
SOLUTION_INTRO = [
    "AmropaliNet puts an expert mango doctor in every farmer's pocket, so that treatment decisions are based on "
    "evidence, not fear.",
    "The farmer takes one photo of a mango with any phone. A CLIP-based check first confirms that the photo "
    "really shows a mango, so a wrong picture never leads to wrong advice. Our AA-ENet model (EfficientNet-B0 "
    "with CBAM attention and a Transformer encoder), trained on 3,500 real Amrapali images, then identifies the "
    "disease - or confirms the fruit is healthy - in seconds. Grad-CAM marks the affected area, so the farmer "
    "can see why the AI decided and trust the result.",
    "Advice comes in simple Bangla or English: treat only the sick trees, with the right product at the right "
    "time, and start with non-chemical steps such as pruning, orchard hygiene, neem oil and hot-water treatment "
    "after harvest. A healthy result means no spray at all. A one-page PDF report can be shown to an "
    "agricultural officer or buyer.",
    "Each decision is small, but together they change the orchard environment:",
]
SOLUTION_POINTS = [
    "Targeted treatment replaces blanket spraying, cutting the chemical load on soil and water (SDG 6, SDG 12).",
    "Fewer sprays at flowering protect bees and orchard biodiversity (SDG 15).",
    "Less exposure protects the health of farming families (SDG 3).",
    "Early detection stops spread, so less fruit - and the water, land and emissions behind it - is wasted "
    "(SDG 12, SDG 13).",
    "Lower costs and saved harvests mean steadier income and more local food (SDG 1, SDG 2).",
]
SOLUTION_END = (
    "AmropaliNet runs free in any browser, works on low-cost phones and is published as the open Python library "
    "mango-disease-ai, so agricultural services and other developers can build on it. "
    "Detect early. Spray less. Waste less."
)

# Environmental harm -> SDG target it works against (UN target wording, shortened)
HARMS = [
    ("Chemical runoff into soil, ponds and groundwater", 6, "6.3", "Improve water quality by reducing pollution and hazardous chemicals"),
    ("Blanket, calendar spraying of agro-chemicals", 12, "12.4", "Sound management of chemicals; less release to air, water and soil"),
    ("Pollinators killed, resistant pathogens bred", 15, "15.5", "Halt the loss of biodiversity"),
    ("Farm families exposed to pesticides", 3, "3.9", "Fewer illnesses from hazardous chemicals and pollution"),
    ("Diseased fruit rots before it is eaten", 12, "12.3", "Reduce food losses along production and supply chains"),
    ("Wasted water, land, fuel and emissions", 13, "13", "Take urgent action to combat climate change and its impacts"),
    ("Lost harvests and income, less local food", 2, "2.4 / 1.5", "Sustainable, resilient food production; resilience of the poor"),
]

CHAIN = [
    ("1", "One photo", "any phone, Bangla or English", []),
    ("2", "Right diagnosis", "mango check, AA-ENet, affected area", []),
    ("3", "Targeted treatment", "only sick trees, non-chemical first", [12, 3]),
    ("4", "Less chemical, less waste", "fewer sprays, less fruit lost", [12, 13, 2]),
    ("5", "Healthier ecosystem", "clean water and soil, safe bees, stable income", [6, 15, 1]),
]

FACTS = [
    ("7", "classes (6 diseases + healthy)"),
    ("3,500", "real Amrapali training images"),
    ("2", "languages: Bangla and English"),
    ("0 Tk", "free in any browser, open library"),
]


def words(parts):
    return sum(len(p.split()) for p in parts)


class Doc(FPDF):
    M = 16

    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(False)
        self.set_margins(self.M, self.M, self.M)
        self.add_font("Hind", "", str(FONTS / "HindSiliguri-Regular.ttf"))
        self.add_font("Hind", "B", str(FONTS / "HindSiliguri-Bold.ttf"))
        self.W = 210 - 2 * self.M

    # -- building blocks
    def font(self, size, bold=False, color=DARK):
        self.set_font("Hind", "B" if bold else "", size)
        self.set_text_color(*color)

    def band(self, kicker, title, sub):
        self.set_fill_color(*GREEN)
        self.rect(0, 0, 210, 38, "F")
        self.set_fill_color(*MANGO)
        self.rect(0, 38, 210, 1.6, "F")
        self.set_xy(self.M, 8)
        self.font(9, True, (255, 214, 120))
        self.cell(self.W, 5, kicker.upper())
        self.set_xy(self.M, 14)
        self.font(21, True, (255, 255, 255))
        self.cell(self.W, 10, title)
        self.set_xy(self.M, 25)
        self.font(10, False, (222, 240, 214))
        self.cell(self.W, 6, sub)
        self.set_y(46)

    def heading(self, text, count=None):
        y = self.get_y()
        self.set_fill_color(*MANGO)
        self.rect(self.M, y + 1.2, 1.6, 6, "F")
        self.set_xy(self.M + 4, y)
        self.font(14, True, GREEN)
        self.cell(0, 8.5, text)
        if count:
            label = f"{count} words"
            self.font(8.5, True, GREEN)
            w = self.get_string_width(label) + 7
            self.set_fill_color(*TINT)
            self.set_draw_color(*LINE)
            self.rect(self.M + self.W - w, y + 1.4, w, 5.6, "DF", round_corners=True, corner_radius=2.8)
            self.set_xy(self.M + self.W - w, y + 1.4)
            self.cell(w, 5.6, label, align="C")
        self.set_y(y + 10.5)

    def para(self, text, size=10.4, gap=2.2, x=None, w=None, color=DARK, lh=5.05):
        self.font(size, False, color)
        self.set_x(x if x is not None else self.M)
        self.multi_cell(w or self.W, lh, text, align="J")
        self.ln(gap)

    def bullets(self, items, size=10.4, lh=5.05):
        for item in items:
            y = self.get_y()
            self.set_fill_color(*GREEN)
            self.ellipse(self.M + 1.2, y + 1.9, 1.7, 1.7, "F")
            self.font(size)
            self.set_xy(self.M + 5, y)
            self.multi_cell(self.W - 5, lh, item, align="L")
            self.ln(0.8)
        self.ln(1.4)

    def sdg_badge(self, x, y, n, h=5.2, full=False):
        name, color = SDG[n]
        label = f"SDG {n}" + (f" {name}" if full else "")
        self.font(7.6 if not full else 7.8, True, (255, 255, 255))
        w = self.get_string_width(label) + 4.5
        self.set_fill_color(*color)
        self.rect(x, y, w, h, "F", round_corners=True, corner_radius=1.4)
        self.set_xy(x, y)
        self.cell(w, h, label, align="C")
        return w

    def footer_line(self, page):
        self.set_draw_color(*LINE)
        self.line(self.M, 283, 210 - self.M, 283)
        self.set_xy(self.M, 284.5)
        self.font(8, False, SOFT)
        self.cell(self.W - 20, 5, "AmropaliNet - AIUB Student Group (Arpon, Oni, Md. Ibtihazzaman) - "
                  "Supervisor: Dr. Md. Saef Ullah Miah - arponamit.55@gmail.com")
        self.cell(20, 5, f"Page {page} of 2", align="R")


def build():
    d = Doc()

    # ============================ PAGE 1 - PROBLEM
    d.add_page()
    d.band("Environment Hackathon - Problem Statement",
           "AmropaliNet: Detect early. Spray less. Waste less.",
           "AI mango doctor for the Amrapali farmers of Bangladesh - protecting orchards, soil, water and bees")
    d.heading("Problem Statement", words(PROBLEM))
    for p in PROBLEM[:-1]:
        d.para(p)

    # root cause callout
    y = d.get_y() + 0.5
    d.font(10.4, False)
    lines = d.multi_cell(d.W - 12, 5.05, PROBLEM[-1], dry_run=True, output="LINES")
    h = len(lines) * 5.05 + 10
    d.set_fill_color(*RED_TINT)
    d.rect(d.M, y, d.W, h, "F", round_corners=True, corner_radius=3)
    d.set_fill_color(*RED)
    d.rect(d.M, y, 1.8, h, "F")
    d.set_xy(d.M + 6, y + 2.2)
    d.font(9, True, RED)
    d.cell(0, 4.5, "ROOT CAUSE")
    d.set_xy(d.M + 6, y + 7)
    d.font(10.4, False, DARK)
    d.multi_cell(d.W - 12, 5.05, PROBLEM[-1], align="J")
    d.set_y(y + h + 5)

    # harm -> SDG table
    d.heading("Environmental harm and the SDG targets it violates")
    col = [62, 22, d.W - 84]
    y = d.get_y()
    d.set_fill_color(*GREEN)
    d.rect(d.M, y, d.W, 6.5, "F")
    d.font(8.6, True, (255, 255, 255))
    x = d.M
    for w, label in zip(col, ["Environmental problem", "SDG", "Target that is violated"]):
        d.set_xy(x + 2.5, y)
        d.cell(w - 2.5, 6.5, label)
        x += w
    y += 6.5
    lh = 4.3
    for i, (harm, n, target, text) in enumerate(HARMS):
        d.font(8.8, True)
        l1 = len(d.multi_cell(col[0] - 5, lh, harm, dry_run=True, output="LINES"))
        d.font(8.6)
        l3 = len(d.multi_cell(col[2] - 19, lh, text, dry_run=True, output="LINES"))
        rh = max(l1, l3, 1) * lh + 4
        d.set_fill_color(*(TINT if i % 2 == 0 else (255, 255, 255)))
        d.rect(d.M, y, d.W, rh, "F")
        d.set_xy(d.M + 2.5, y + 2)
        d.font(8.8, True, DARK)
        d.multi_cell(col[0] - 5, lh, harm, align="L")
        d.sdg_badge(d.M + col[0], y + rh / 2 - 2.6, n)
        d.set_xy(d.M + col[0] + col[1], y + 2)
        d.font(8.6, True, SDG[n][1] if n not in (2, 12) else (150, 105, 20))
        d.cell(17, lh, target)
        d.set_xy(d.M + col[0] + col[1] + 17, y + 2)
        d.font(8.6, False, SOFT)
        d.multi_cell(col[2] - 19, lh, text, align="L")
        y += rh
    d.set_draw_color(*LINE)
    d.line(d.M, y, d.M + d.W, y)
    d.footer_line(1)

    # ============================ PAGE 2 - SOLUTION
    d.add_page()
    d.band("Environment Hackathon - Solution",
           "AmropaliNet: the right treatment, only where needed",
           "One photo -> the right diagnosis -> less chemical and less waste -> a healthier environment")
    total = words(SOLUTION_INTRO) + words(SOLUTION_POINTS) + words([SOLUTION_END])
    d.heading("Solution", total)
    for p in SOLUTION_INTRO[:-1]:
        d.para(p)
    d.font(10.4, True, GREEN)
    d.set_x(d.M)
    d.multi_cell(d.W, 5.05, SOLUTION_INTRO[-1])
    d.ln(1.2)
    d.bullets(SOLUTION_POINTS)
    d.para(SOLUTION_END, gap=4)

    # impact chain
    d.heading("How everything connects: from one photo to the SDGs")
    y = d.get_y() + 1
    n = len(CHAIN)
    gap = 4.2
    bw = (d.W - gap * (n - 1)) / n
    bh = 33
    for i, (num, title, sub, goals) in enumerate(CHAIN):
        x = d.M + i * (bw + gap)
        last = i == n - 1
        d.set_fill_color(*(GREEN if last else TINT))
        d.set_draw_color(*LINE)
        d.rect(x, y, bw, bh, "DF", round_corners=True, corner_radius=3)
        d.set_fill_color(*MANGO)
        d.ellipse(x + bw / 2 - 3.2, y + 2.2, 6.4, 6.4, "F")
        d.set_xy(x + bw / 2 - 3.2, y + 2.2)
        d.font(9, True, (255, 255, 255))
        d.cell(6.4, 6.4, num, align="C")
        d.set_xy(x + 1.5, y + 9.5)
        d.font(8.9, True, (255, 255, 255) if last else DARK)
        d.multi_cell(bw - 3, 4.1, title, align="C")
        d.set_x(x + 1.5)
        d.font(7.6, False, (225, 242, 218) if last else SOFT)
        d.multi_cell(bw - 3, 3.5, sub, align="C")
        if not last:  # arrow
            ax = x + bw + 0.6
            d.set_fill_color(*MANGO)
            d.polygon([(ax, y + bh / 2 - 2.2), (ax + gap - 1.2, y + bh / 2), (ax, y + bh / 2 + 2.2)], style="F")
        bx, by = x, y + bh + 2
        for g in goals:
            d.font(7.6, True)
            need = d.get_string_width(f"SDG {g}") + 4.5
            if bx + need > x + bw + 0.1:
                bx, by = x, by + 5.6
            bx += d.sdg_badge(bx, by, g, h=4.6) + 1
    d.set_y(y + bh + 15)

    # key facts row
    fw = (d.W - 3 * 3) / 4
    y = d.get_y()
    for i, (big, small) in enumerate(FACTS):
        x = d.M + i * (fw + 3)
        d.set_fill_color(*TINT)
        d.rect(x, y, fw, 15, "F", round_corners=True, corner_radius=2.5)
        d.set_xy(x, y + 1.6)
        d.font(13, True, MANGO)
        d.cell(fw, 6.5, big, align="C")
        d.set_xy(x, y + 8)
        d.font(7.8, False, SOFT)
        d.cell(fw, 5, small, align="C")
    d.set_y(y + 19)

    # SDGs advanced
    d.font(9.5, True, GREEN)
    d.set_x(d.M)
    d.cell(0, 6, "SDGs AmropaliNet advances:")
    d.ln(7)
    x = d.M
    for g in (1, 2, 3, 6, 12, 13, 15):
        w = d.sdg_badge(x, d.get_y(), g, h=6, full=True)
        x += w + 1.8
        if x > d.M + d.W - 30:
            x = d.M
            d.set_y(d.get_y() + 7.5)
    d.footer_line(2)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    d.output(str(OUT))
    return words(PROBLEM), total


if __name__ == "__main__":
    p, s = build()
    print(f"Saved {OUT}  (problem {p} words, solution {s} words)")
