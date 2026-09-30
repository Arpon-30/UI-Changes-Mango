"""Build the problem statement + solution PDFs (environment and SDG focus), English and Bangla.

Run:  python docs/build_problem_solution.py
Makes, in docs/:
  AmropaliNet_Problem_Solution.pdf     4 pages: English (1-2) + Bangla (3-4)
  AmropaliNet_Problem_Solution_EN.pdf  2 pages, English only
  AmropaliNet_Problem_Solution_BN.pdf  2 pages, Bangla only
Needs fpdf2 and uharfbuzz (both in api/requirements.txt). Uses the bundled Hind Siliguri font.
Bangla lines are wrapped by hand: fpdf2's multi_cell mis-shapes wrapped Bangla lines.
"""
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "mango_disease_ai" / "fonts"
DOCS = ROOT / "docs"

GREEN = (46, 125, 50)
DARK = (29, 58, 31)
SOFT = (84, 104, 86)
MANGO = (239, 138, 0)
GOLD_TEXT = (150, 105, 20)
TINT = (241, 247, 234)
LINE = (214, 228, 205)
RED = (190, 55, 45)
RED_TINT = (252, 236, 233)
WHITE = (255, 255, 255)

# Official UN SDG colours, short names in English and Bangla
SDG = {
    1: ((229, 36, 59), "No Poverty", "দারিদ্র্য বিলোপ"),
    2: ((221, 166, 58), "Zero Hunger", "ক্ষুধামুক্তি"),
    3: ((76, 159, 56), "Good Health", "সুস্বাস্থ্য"),
    6: ((38, 189, 226), "Clean Water", "নিরাপদ পানি"),
    12: ((191, 139, 46), "Responsible Production", "দায়িত্বশীল উৎপাদন"),
    13: ((63, 126, 68), "Climate Action", "জলবায়ু কার্যক্রম"),
    15: ((86, 192, 43), "Life on Land", "স্থলজ জীবন"),
}

BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

# ─────────────────────────────────────────────────────────────── content
TEXT = {
    "en": {
        "p1_kicker": "Environment Hackathon - Problem Statement",
        "p1_title": "AmropaliNet: Detect early. Spray less. Waste less.",
        "p1_sub": "AI mango doctor for the Amrapali farmers of Bangladesh - protecting orchards, soil, water and bees",
        "problem_h": "Problem Statement",
        "problem": [
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
        ],
        "root_h": "ROOT CAUSE",
        "root": "The root cause is one missing piece of knowledge at the right moment: which disease is this, and what is "
                "the smallest treatment that works? Without it, farmers overspray, lose fruit and damage the ecosystem "
                "their orchards depend on - season after season.",
        "table_h": "Environmental harm and the SDG targets it violates",
        "table_cols": ["Environmental problem", "SDG", "Target that is violated"],
        "harms": [
            ("Chemical runoff into soil, ponds and groundwater", 6, "6.3", "Improve water quality by reducing pollution and hazardous chemicals"),
            ("Blanket, calendar spraying of agro-chemicals", 12, "12.4", "Sound management of chemicals; less release to air, water and soil"),
            ("Pollinators killed, resistant pathogens bred", 15, "15.5", "Halt the loss of biodiversity"),
            ("Farm families exposed to pesticides", 3, "3.9", "Fewer illnesses from hazardous chemicals and pollution"),
            ("Diseased fruit rots before it is eaten", 12, "12.3", "Reduce food losses along production and supply chains"),
            ("Wasted water, land, fuel and emissions", 13, "13", "Take urgent action to combat climate change and its impacts"),
            ("Lost harvests and income, less local food", 2, "2.4 / 1.5", "Sustainable, resilient food production; resilience of the poor"),
        ],
        "who": [
            ("Where", "Rajshahi, Chapainawabganj, Naogaon and the hill districts"),
            ("Who is affected", "small mango farmers, farm workers, consumers, bees and orchard wildlife"),
        ],
        "p2_kicker": "Environment Hackathon - Solution",
        "p2_title": "AmropaliNet: the right treatment, only where needed",
        "p2_sub": "One photo, the right diagnosis, less chemical and less waste - a healthier environment",
        "solution_h": "Solution",
        "solution": [
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
        ],
        "lead": "Each decision is small, but together they change the orchard environment:",
        "points": [
            "Targeted treatment replaces blanket spraying, cutting the chemical load on soil and water (SDG 6, SDG 12).",
            "Fewer sprays at flowering protect bees and orchard biodiversity (SDG 15).",
            "Less exposure protects the health of farming families (SDG 3).",
            "Early detection stops spread, so less fruit - and the water, land and emissions behind it - is wasted "
            "(SDG 12, SDG 13).",
            "Lower costs and saved harvests mean steadier income and more local food (SDG 1, SDG 2).",
        ],
        "end": "AmropaliNet runs free in any browser, works on low-cost phones and is published as the open Python "
               "library mango-disease-ai, so agricultural services and other developers can build on it. "
               "Detect early. Spray less. Waste less.",
        "chain_h": "How everything connects: from one photo to the SDGs",
        "chain": [
            ("One photo", "any phone, Bangla or English", []),
            ("Right diagnosis", "mango check, AA-ENet, affected area", []),
            ("Targeted treatment", "only sick trees, non-chemical first", [12, 3]),
            ("Less chemical, less waste", "fewer sprays, less fruit lost", [12, 13, 2]),
            ("Healthier ecosystem", "clean water and soil, safe bees, stable income", [6, 15, 1]),
        ],
        "facts": [
            ("7", "classes (6 diseases + healthy)"),
            ("3,500", "real Amrapali training images"),
            ("2", "languages: Bangla and English"),
            ("Free", "in any browser, open library"),
        ],
        "sdg_h": "SDGs AmropaliNet advances:",
        "words": "{} words",
        "footer": "AmropaliNet - AIUB Student Group (Arpon, Oni, Md. Ibtihazzaman) - "
                  "Supervisor: Dr. Md. Saef Ullah Miah - arponamit.55@gmail.com",
        "page": "Page {} of {}",
    },
    "bn": {
        "p1_kicker": "পরিবেশ হ্যাকাথন - সমস্যা বিবৃতি",
        "p1_title": "আম্রপালিনেট: আগে শনাক্ত, কম স্প্রে, কম অপচয়",
        "p1_sub": "বাংলাদেশের আম্রপালি চাষিদের জন্য এআই আম ডাক্তার - বাগান, মাটি, পানি ও মৌমাছি রক্ষায়",
        "problem_h": "সমস্যা বিবৃতি",
        "problem": [
            "আম্রপালি বাংলাদেশের সবচেয়ে প্রিয় দৈনন্দিন আম এবং রাজশাহী, চাঁপাইনবাবগঞ্জ, নওগাঁ ও পার্বত্য জেলার হাজারো "
            "কৃষক পরিবারের আয়ের প্রধান উৎস। প্রতি মৌসুমে এই আমে ছয়টি সাধারণ রোগ আক্রমণ করে: অ্যানথ্রাকনোজ, "
            "ব্যাকটেরিয়াল ক্যাঙ্কার, পাউডারি মিলডিউ, স্ক্যাব, সুটি মোল্ড ও বোঁটা পচা।",
            "বেশিরভাগ কৃষক রোগগুলো আলাদা করে চিনতে পারেন না, আর প্রথম দাগ দেখা দেওয়ার সময় কৃষি কর্মকর্তাকে কাছে "
            "পাওয়া যায় না। তাই সাধারণ সমাধান হয় ক্যালেন্ডার মেনে ঢালাও স্প্রে: \"যদি লাগে\" ভেবে পুরো বাগানে একাধিক "
            "ছত্রাকনাশক ও কীটনাশক ছিটানো হয়, মুকুল থেকে ফল পাড়া পর্যন্ত বারবার।",
            "এভাবেই একটি কৃষি সমস্যা পরিবেশের সমস্যায় পরিণত হয়। বাড়তি রাসায়নিক মাটি, পুকুর ও ভূগর্ভস্থ পানিতে মিশে "
            "জলজ প্রাণী ও গ্রামের খাবার পানির ক্ষতি করে (SDG 6)। মুকুলের সময় স্প্রে করলে ফল ধরাতে প্রয়োজনীয় মৌমাছি ও "
            "অন্যান্য পরাগায়নকারী মারা যায়, আর বারবার প্রয়োগে রোগজীবাণু ওষুধ-প্রতিরোধী হয়ে ওঠে (SDG 15)। কৃষক ও তাঁদের "
            "পরিবার প্রায়ই কোনো সুরক্ষা ছাড়াই এই রাসায়নিক শ্বাসে নেন ও হাতে ধরেন (SDG 3)।",
            "দ্বিতীয় সমস্যা অপচয়। দেরিতে রোগ ধরা পড়লে তা ততক্ষণে ছড়িয়ে যায়, আর আক্রান্ত ফল গাছে, গুদামে বা পরিবহনে "
            "পচে যায়। প্রতিটি ফেলে দেওয়া আম মানে তা ফলাতে খরচ হওয়া পানি, জমি, সার, জ্বালানি ও শ্রমের অপচয়, আর পচা "
            "ফল থেকে গ্রিনহাউস গ্যাস নির্গত হয় (SDG 12, SDG 13)। হারানো ফসল ও অপ্রয়োজনীয় রাসায়নিকের খরচ ক্ষুদ্র "
            "কৃষককে দারিদ্র্যের দিকে ঠেলে দেয় এবং স্থানীয় খাদ্যের জোগান কমায় (SDG 1, SDG 2)।",
        ],
        "root_h": "মূল কারণ",
        "root": "মূল কারণ হলো সঠিক সময়ে একটি জরুরি তথ্যের অভাব: এটি কোন রোগ, আর কাজ করবে এমন সবচেয়ে ছোট চিকিৎসা "
                "কোনটি? এই তথ্য ছাড়া কৃষক বাড়তি স্প্রে করেন, ফল হারান এবং যে প্রকৃতির উপর তাঁর বাগান নির্ভর করে, "
                "মৌসুমের পর মৌসুম সেটিরই ক্ষতি করেন।",
        "table_h": "পরিবেশগত ক্ষতি ও যে SDG লক্ষ্যমাত্রা লঙ্ঘিত হচ্ছে",
        "table_cols": ["পরিবেশগত সমস্যা", "SDG", "যে লক্ষ্যমাত্রা লঙ্ঘিত হচ্ছে"],
        "harms": [
            ("মাটি, পুকুর ও ভূগর্ভস্থ পানিতে রাসায়নিক মেশা", 6, "6.3", "দূষণ ও ক্ষতিকর রাসায়নিক কমিয়ে পানির মান উন্নত করা"),
            ("ক্যালেন্ডার মেনে ঢালাও রাসায়নিক স্প্রে", 12, "12.4", "রাসায়নিকের নিরাপদ ব্যবস্থাপনা; বাতাস, পানি ও মাটিতে নিঃসরণ কমানো"),
            ("পরাগায়নকারী মারা যাওয়া, ওষুধ-প্রতিরোধী জীবাণু", 15, "15.5", "জীববৈচিত্র্যের ক্ষতি বন্ধ করা"),
            ("কৃষক পরিবারের কীটনাশকের সংস্পর্শ", 3, "3.9", "ক্ষতিকর রাসায়নিক ও দূষণজনিত অসুস্থতা কমানো"),
            ("খাওয়ার আগেই রোগাক্রান্ত ফল পচে যাওয়া", 12, "12.3", "উৎপাদন ও সরবরাহ শৃঙ্খলে খাদ্যের ক্ষতি কমানো"),
            ("পানি, জমি, জ্বালানি ও নির্গমনের অপচয়", 13, "13", "জলবায়ু পরিবর্তন ও এর প্রভাব মোকাবিলায় জরুরি পদক্ষেপ"),
            ("ফসল ও আয় হারানো, স্থানীয় খাদ্য কমা", 2, "2.4 / 1.5", "টেকসই ও সহনশীল খাদ্য উৎপাদন; দরিদ্রদের সহনশীলতা"),
        ],
        "who": [
            ("কোথায়", "রাজশাহী, চাঁপাইনবাবগঞ্জ, নওগাঁ ও পার্বত্য জেলা"),
            ("কারা ক্ষতিগ্রস্ত", "ক্ষুদ্র আমচাষি, কৃষি শ্রমিক, ভোক্তা, মৌমাছি ও বাগানের বন্যপ্রাণী"),
        ],
        "p2_kicker": "পরিবেশ হ্যাকাথন - সমাধান",
        "p2_title": "আম্রপালিনেট: শুধু প্রয়োজনের জায়গায় সঠিক চিকিৎসা",
        "p2_sub": "একটি ছবি, সঠিক রোগ নির্ণয়, কম রাসায়নিক ও কম অপচয় - সুস্থ পরিবেশ",
        "solution_h": "সমাধান",
        "solution": [
            "আম্রপালিনেট প্রতিটি কৃষকের পকেটে একজন দক্ষ আম ডাক্তার পৌঁছে দেয়, যাতে চিকিৎসার সিদ্ধান্ত ভয় থেকে নয়, "
            "প্রমাণ থেকে আসে।",
            "কৃষক যেকোনো ফোনে আমের একটি ছবি তোলেন। প্রথমে CLIP-ভিত্তিক যাচাই নিশ্চিত করে যে ছবিটি সত্যিই আমের, তাই "
            "ভুল ছবি থেকে কখনো ভুল পরামর্শ আসে না। এরপর ৩,৫০০টি আসল আম্রপালি ছবিতে প্রশিক্ষিত আমাদের AA-ENet মডেল "
            "(EfficientNet-B0, CBAM অ্যাটেনশন ও Transformer এনকোডার) কয়েক সেকেন্ডে রোগ শনাক্ত করে, অথবা জানায় যে "
            "আমটি সুস্থ। Grad-CAM আক্রান্ত অংশ চিহ্নিত করে, ফলে কৃষক দেখতে পান এআই কেন এই সিদ্ধান্ত দিল এবং "
            "ফলাফলে ভরসা করতে পারেন।",
            "পরামর্শ আসে সহজ বাংলা বা ইংরেজিতে: শুধু অসুস্থ গাছে, সঠিক সময়ে সঠিক ওষুধ দিন, আর শুরু করুন রাসায়নিক "
            "ছাড়া উপায় দিয়ে, যেমন ডাল ছাঁটাই, বাগান পরিষ্কার রাখা, নিম তেল এবং ফল পাড়ার পর গরম পানিতে শোধন। সুস্থ "
            "ফলাফল মানে কোনো স্প্রেই লাগবে না। এক পাতার পিডিএফ রিপোর্ট কৃষি কর্মকর্তা বা ক্রেতাকে দেখানো যায়।",
        ],
        "lead": "প্রতিটি সিদ্ধান্ত ছোট, কিন্তু সব মিলিয়ে বাগানের পরিবেশ বদলে যায়:",
        "points": [
            "ঢালাও স্প্রের বদলে লক্ষ্যভিত্তিক চিকিৎসা মাটি ও পানিতে রাসায়নিকের চাপ কমায় (SDG 6, SDG 12)।",
            "মুকুলের সময় কম স্প্রে মৌমাছি ও বাগানের জীববৈচিত্র্য রক্ষা করে (SDG 15)।",
            "রাসায়নিকের সংস্পর্শ কমলে কৃষক পরিবারের স্বাস্থ্য সুরক্ষিত থাকে (SDG 3)।",
            "আগেভাগে শনাক্ত করলে রোগ ছড়ায় না, তাই কম ফল নষ্ট হয় - সাথে বাঁচে এর পেছনের পানি, জমি ও নির্গমন "
            "(SDG 12, SDG 13)।",
            "কম খরচ ও রক্ষা পাওয়া ফসল মানে স্থির আয় ও বেশি স্থানীয় খাদ্য (SDG 1, SDG 2)।",
        ],
        "end": "আম্রপালিনেট যেকোনো ব্রাউজারে বিনামূল্যে চলে, কম দামের ফোনেও কাজ করে এবং ওপেন পাইথন লাইব্রেরি "
               "mango-disease-ai হিসেবে প্রকাশিত, তাই কৃষি সেবা ও অন্য ডেভেলপাররাও এর উপর কাজ করতে পারেন। "
               "আগে শনাক্ত করুন। কম স্প্রে করুন। কম অপচয় করুন।",
        "chain_h": "সবকিছু কীভাবে যুক্ত: একটি ছবি থেকে SDG পর্যন্ত",
        "chain": [
            ("একটি ছবি", "যেকোনো ফোন, বাংলা বা ইংরেজি", []),
            ("সঠিক রোগ নির্ণয়", "আম যাচাই, AA-ENet, আক্রান্ত অংশ", []),
            ("লক্ষ্যভিত্তিক চিকিৎসা", "শুধু অসুস্থ গাছ, আগে রাসায়নিকমুক্ত উপায়", [12, 3]),
            ("কম রাসায়নিক, কম অপচয়", "কম স্প্রে, কম ফল নষ্ট", [12, 13, 2]),
            ("সুস্থ বাস্তুতন্ত্র", "পরিষ্কার পানি ও মাটি, নিরাপদ মৌমাছি, স্থির আয়", [6, 15, 1]),
        ],
        "facts": [
            ("৭", "শ্রেণি (৬টি রোগ + সুস্থ)"),
            ("৩,৫০০", "আসল আম্রপালি প্রশিক্ষণ ছবি"),
            ("২", "ভাষা: বাংলা ও ইংরেজি"),
            ("বিনামূল্যে", "যেকোনো ব্রাউজারে, ওপেন লাইব্রেরি"),
        ],
        "sdg_h": "আম্রপালিনেট যে SDG-গুলো এগিয়ে নেয়:",
        "words": "{} শব্দ",
        "footer": "AmropaliNet - AIUB Student Group (Arpon, Oni, Md. Ibtihazzaman) - "
                  "Supervisor: Dr. Md. Saef Ullah Miah - arponamit.55@gmail.com",
        "page": "পৃষ্ঠা {} / {}",
    },
}


def count_words(parts):
    return sum(len(p.split()) for p in parts)


def problem_words(t):
    return count_words(t["problem"] + [t["root"]])


def solution_words(t):
    return count_words(t["solution"] + [t["lead"]] + t["points"] + [t["end"]])


class Doc(FPDF):
    M = 16

    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(False)
        self.set_margins(self.M, self.M, self.M)
        self.add_font("Hind", "", str(FONTS / "HindSiliguri-Regular.ttf"))
        self.add_font("Hind", "B", str(FONTS / "HindSiliguri-Bold.ttf"))
        self.set_text_shaping(True)
        self.W = 210 - 2 * self.M
        self.lang = "en"

    # ---- text helpers
    def num(self, n):
        s = str(n)
        return s.translate(BN_DIGITS) if self.lang == "bn" else s

    def font(self, size, bold=False, color=DARK):
        self.set_font("Hind", "B" if bold else "", size)
        self.set_text_color(*color)

    def wrap(self, text, width):
        lines, cur = [], ""
        for word in str(text).split():
            cand = f"{cur} {word}".strip()
            if not cur or self.get_string_width(cand) <= width:
                cur = cand
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def lines_at(self, text, x, y, w, lh, align="L"):
        """Draw wrapped text line by line (current font). Returns the y below it."""
        for line in self.wrap(text, w):
            self.set_xy(x, y)
            self.cell(w, lh, line, align=align)
            y += lh
        return y

    def para(self, text, size=10.4, lh=5.05, gap=2.2, color=DARK, bold=False):
        self.font(size, bold, color)
        if self.lang == "en" and not bold:
            self.set_x(self.M)
            self.multi_cell(self.W, lh, text, align="J")
            self.set_y(self.get_y() + gap)
        else:
            self.set_y(self.lines_at(text, self.M, self.get_y(), self.W, lh) + gap)

    # ---- page parts
    def band(self, kicker, title, sub):
        self.set_fill_color(*GREEN)
        self.rect(0, 0, 210, 38, "F")
        self.set_fill_color(*MANGO)
        self.rect(0, 38, 210, 1.6, "F")
        self.set_xy(self.M, 7.5)
        self.font(9, True, (255, 214, 120))
        self.cell(self.W, 5, kicker.upper() if self.lang == "en" else kicker)
        self.set_xy(self.M, 13.5)
        self.font(20 if self.lang == "en" else 19, True, WHITE)
        self.cell(self.W, 10, title)
        self.set_xy(self.M, 25)
        self.font(9.8, False, (222, 240, 214))
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
            label = TEXT[self.lang]["words"].format(self.num(count))
            self.font(8.5, True, GREEN)
            w = self.get_string_width(label) + 7
            self.set_fill_color(*TINT)
            self.set_draw_color(*LINE)
            self.rect(self.M + self.W - w, y + 1.4, w, 5.6, "DF", round_corners=True, corner_radius=2.8)
            self.set_xy(self.M + self.W - w, y + 1.4)
            self.cell(w, 5.6, label, align="C")
        self.set_y(y + 10.5)

    def sdg_badge(self, x, y, n, h=5.2, full=False):
        color, en, bn = SDG[n]
        label = f"SDG {n}" + (f" {en if self.lang == 'en' else bn}" if full else "")
        self.font(7.6 if not full else 7.8, True, WHITE)
        w = self.get_string_width(label) + 4.5
        self.set_fill_color(*color)
        self.rect(x, y, w, h, "F", round_corners=True, corner_radius=1.4)
        self.set_xy(x, y)
        self.cell(w, h, label, align="C")
        return w

    def footer_line(self, page, total):
        t = TEXT[self.lang]
        self.set_draw_color(*LINE)
        self.line(self.M, 283, 210 - self.M, 283)
        self.set_xy(self.M, 284.5)
        self.font(8, False, SOFT)
        self.cell(self.W - 24, 5, t["footer"])
        self.cell(24, 5, t["page"].format(self.num(page), self.num(total)), align="R")

    # ---- pages
    def problem_page(self, page, total):
        t = TEXT[self.lang]
        self.add_page()
        self.band(t["p1_kicker"], t["p1_title"], t["p1_sub"])
        self.heading(t["problem_h"], problem_words(t))
        for p in t["problem"]:
            self.para(p)

        # root cause callout
        y = self.get_y() + 0.5
        self.font(10.4)
        lines = self.wrap(t["root"], self.W - 12)
        h = len(lines) * 5.05 + 11
        self.set_fill_color(*RED_TINT)
        self.rect(self.M, y, self.W, h, "F", round_corners=True, corner_radius=3)
        self.set_fill_color(*RED)
        self.rect(self.M, y, 1.8, h, "F")
        self.set_xy(self.M + 6, y + 2.2)
        self.font(9, True, RED)
        self.cell(0, 4.5, t["root_h"])
        self.font(10.4, False, DARK)
        self.lines_at(t["root"], self.M + 6, y + 8, self.W - 12, 5.05)
        self.set_y(y + h + 5)

        # harm -> SDG table
        self.heading(t["table_h"])
        col = [62, 22, self.W - 84]
        y = self.get_y()
        self.set_fill_color(*GREEN)
        self.rect(self.M, y, self.W, 6.5, "F")
        self.font(8.6, True, WHITE)
        x = self.M
        for w, label in zip(col, t["table_cols"]):
            self.set_xy(x + 2.5, y)
            self.cell(w - 2.5, 6.5, label)
            x += w
        y += 6.5
        lh = 4.3
        for i, (harm, n, target, text) in enumerate(t["harms"]):
            self.font(8.8, True)
            l1 = self.wrap(harm, col[0] - 5)
            self.font(8.6)
            l3 = self.wrap(text, col[2] - 19)
            rh = max(len(l1), len(l3), 1) * lh + 4
            self.set_fill_color(*(TINT if i % 2 == 0 else WHITE))
            self.rect(self.M, y, self.W, rh, "F")
            self.font(8.8, True, DARK)
            self.lines_at(harm, self.M + 2.5, y + 2, col[0] - 5, lh)
            self.sdg_badge(self.M + col[0], y + rh / 2 - 2.6, n)
            self.set_xy(self.M + col[0] + col[1], y + 2)
            self.font(8.6, True, SDG[n][0] if n not in (2, 12) else GOLD_TEXT)
            self.cell(17, lh, self.num(target))
            self.font(8.6, False, SOFT)
            self.lines_at(text, self.M + col[0] + col[1] + 17, y + 2, col[2] - 19, lh)
            y += rh
        self.set_draw_color(*LINE)
        self.line(self.M, y, self.M + self.W, y)

        # where / who strip
        y += 5
        for label, value in t["who"]:
            self.font(9.2, True, GREEN)
            lw = self.get_string_width(label + ":") + 2
            self.set_xy(self.M, y)
            self.cell(lw, 5, label + ":")
            self.font(9.2, False, DARK)
            y = self.lines_at(value, self.M + lw, y, self.W - lw, 5) + 1
        self.footer_line(page, total)

    def solution_page(self, page, total):
        t = TEXT[self.lang]
        self.add_page()
        self.band(t["p2_kicker"], t["p2_title"], t["p2_sub"])
        self.heading(t["solution_h"], solution_words(t))
        for p in t["solution"]:
            self.para(p)
        self.para(t["lead"], bold=True, color=GREEN, gap=1.2)
        for item in t["points"]:
            y = self.get_y()
            self.set_fill_color(*GREEN)
            self.ellipse(self.M + 1.2, y + 1.9, 1.7, 1.7, "F")
            self.font(10.4)
            self.set_y(self.lines_at(item, self.M + 5, y, self.W - 5, 5.05) + 0.8)
        self.set_y(self.get_y() + 1.4)
        self.para(t["end"], gap=4)

        # impact chain
        self.heading(t["chain_h"])
        y = self.get_y() + 1
        n = len(t["chain"])
        gap = 4.2
        bw = (self.W - gap * (n - 1)) / n
        bh = 33
        for i, (title, sub, goals) in enumerate(t["chain"]):
            x = self.M + i * (bw + gap)
            last = i == n - 1
            self.set_fill_color(*(GREEN if last else TINT))
            self.set_draw_color(*LINE)
            self.rect(x, y, bw, bh, "DF", round_corners=True, corner_radius=3)
            self.set_fill_color(*MANGO)
            self.ellipse(x + bw / 2 - 3.2, y + 2.2, 6.4, 6.4, "F")
            self.set_xy(x + bw / 2 - 3.2, y + 2.2)
            self.font(9, True, WHITE)
            self.cell(6.4, 6.4, self.num(i + 1), align="C")
            self.font(8.9, True, WHITE if last else DARK)
            ty = self.lines_at(title, x + 1.5, y + 9.5, bw - 3, 4.1, align="C")
            self.font(7.6, False, (225, 242, 218) if last else SOFT)
            self.lines_at(sub, x + 1.5, ty + 0.3, bw - 3, 3.6, align="C")
            if not last:  # arrow to the next box
                ax = x + bw + 0.6
                self.set_fill_color(*MANGO)
                self.polygon([(ax, y + bh / 2 - 2.2), (ax + gap - 1.2, y + bh / 2), (ax, y + bh / 2 + 2.2)], style="F")
            bx, by = x, y + bh + 2
            for g in goals:
                self.font(7.6, True)
                need = self.get_string_width(f"SDG {g}") + 4.5
                if bx + need > x + bw + 0.1:
                    bx, by = x, by + 5.6
                bx += self.sdg_badge(bx, by, g, h=4.6) + 1
        self.set_y(y + bh + 15)

        # key facts
        fw = (self.W - 3 * 3) / 4
        y = self.get_y()
        for i, (big, small) in enumerate(t["facts"]):
            x = self.M + i * (fw + 3)
            self.set_fill_color(*TINT)
            self.rect(x, y, fw, 15, "F", round_corners=True, corner_radius=2.5)
            self.set_xy(x, y + 1.6)
            self.font(13, True, MANGO)
            self.cell(fw, 6.5, big, align="C")
            self.set_xy(x, y + 8)
            self.font(7.8, False, SOFT)
            self.cell(fw, 5, small, align="C")
        self.set_y(y + 19)

        # SDGs advanced
        self.font(9.5, True, GREEN)
        self.set_x(self.M)
        self.cell(0, 6, t["sdg_h"])
        self.set_y(self.get_y() + 7)
        x = self.M
        for g in (1, 2, 3, 6, 12, 13, 15):
            self.font(7.8, True)
            color, en, bn = SDG[g]
            need = self.get_string_width(f"SDG {g} {en if self.lang == 'en' else bn}") + 4.5
            if x + need > self.M + self.W:
                x = self.M
                self.set_y(self.get_y() + 7.5)
            x += self.sdg_badge(x, self.get_y(), g, h=6, full=True) + 1.8
        self.footer_line(page, total)


def build(langs, out):
    d = Doc()
    total = 2 * len(langs)
    for i, lang in enumerate(langs):
        d.lang = lang
        d.problem_page(2 * i + 1, total)
        d.solution_page(2 * i + 2, total)
    d.output(str(out))
    return out


if __name__ == "__main__":
    for lang in ("en", "bn"):
        t = TEXT[lang]
        print(f"{lang}: problem {problem_words(t)} words, solution {solution_words(t)} words")
    for langs, name in ((("en", "bn"), "AmropaliNet_Problem_Solution.pdf"),
                        (("en",), "AmropaliNet_Problem_Solution_EN.pdf"),
                        (("bn",), "AmropaliNet_Problem_Solution_BN.pdf")):
        print("Saved", build(langs, DOCS / name))
