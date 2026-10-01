"""Editable PDF deck source. Run with ReportLab and Pillow available."""

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission/Ipon_Buffer_Pitch.pdf"
FONT_DIR = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", str(FONT_DIR / "arial.ttf")))
pdfmetrics.registerFont(TTFont("ArialBold", str(FONT_DIR / "arialbd.ttf")))
c = Canvas(str(OUT), pagesize=(1280, 720))
c.setTitle("Ipon Buffer - synthetic prototype pitch")
c.setAuthor("Applicant identity pending")
CREAM, GREEN, INK, MUTED = "#F6F5EF", "#224E3E", "#172B29", "#5D6D61"
page = 0


def text(value, x, y, width, size=29, color=INK, bold=False, leading=None):
    font = "ArialBold" if bold else "Arial"
    c.setFillColor(HexColor(color))
    c.setFont(font, size)
    lines = []
    for paragraph in value.split("\n"):
        lines.extend(simpleSplit(paragraph, font, size, width) if paragraph else [""])
    for i, line in enumerate(lines):
        baseline = 720 - y - size - i * (leading or size * 1.35)
        if baseline < 20:
            raise ValueError(f"Text exceeds slide {page}: {value}")
        c.drawString(x, baseline, line)


def slide(title, dark=False):
    global page
    if page:
        c.showPage()
    page += 1
    c.setFillColor(HexColor(GREEN if dark else CREAM))
    c.rect(0, 0, 1280, 720, fill=1, stroke=0)
    if title:
        text(title, 68, 48, 1140, 42, "#FFFFFF" if dark else INK, True)
    text(str(page), 1195, 665, 40, 18, "#D4E0CA" if dark else MUTED)


def foot(value):
    text(value, 68, 632, 1080, 20, MUTED)


def table(values, x, y, widths, row_height=61):
    for r, row in enumerate(values):
        offset = x
        for col, value in enumerate(row):
            c.setFillColor(HexColor(GREEN if r == 0 else ("#FFFFFF" if r % 2 else "#E7ECDD")))
            c.rect(offset, 720-y-(r+1)*row_height, widths[col], row_height, fill=1, stroke=0)
            text(value, offset+15, y+r*row_height+12, widths[col]-25, 23,
                 "#FFFFFF" if r == 0 else INK, r == 0, 27)
            offset += widths[col]


slide("", True)
text("Ipon Buffer", 68, 105, 1140, 78, "#FFFFFF", True)
text("A savings plan that starts\nwith what your money needs to cover.", 68, 247, 1120, 43, "#E3ECD8")
text("For Philippine workers with irregular income", 68, 457, 1110, 29, "#FFFFFF")
text("Working synthetic prototype. Mock wallet.\nExperimental local AI, with mandatory review.", 68, 586, 1110, 23, "#D4E0CA")

slide("A payment today has several jobs tomorrow.")
text("PHP 2,000", 68, 210, 560, 66, GREEN, True)
text("available after an income payment", 68, 308, 560, 28, MUTED)
text("PHP 250 per day for essentials\nPHP 600 bill due September 30\nNext income expected October 2", 672, 220, 540, 28)
text("How much can be set aside while leaving room\nfor the confirmed essentials?", 68, 466, 1120, 35)
foot("Illustrative September 28, 2026 scenario. Future income and omitted expenses remain uncertain.")

slide("The user reviews every plan and every deposit.")
steps = [("1. Describe or enter", "Upcoming bills and expected income."),
         ("2. Review and confirm", "Check amounts, dates and double counting."),
         ("3. Choose a deposit", "The engine protects planned essentials first."),
         ("4. Access and rebuild", "Withdraw, then consider an optional refill.")]
for i, (title, detail) in enumerate(steps):
    x, y = 68+(i % 2)*600, 210+(i // 2)*190
    text(title, x, y, 530, 32, GREEN, True)
    text(detail, x, y+64, 520, 28)
foot("Manual and local AI entry demonstrated. AI drafts fields and has no money-moving tools.")

slide("One omitted bill changes PHP 120 to PHP 0.")
table([["Confirmed plan", "Before", "After school bill"],
       ["Everyday needs, 4 days", "PHP 1,000", "PHP 1,000"],
       ["Bills due", "PHP 600", "PHP 900"],
       ["Reserve, with 10% margin", "PHP 1,760", "PHP 2,090"],
       ["Suggested deposit", "PHP 120", "PHP 0"]], 68, 198, [550, 270, 320])
text("The user adds PHP 300 due tomorrow.\nThe engine recalculates before money can move.", 68, 531, 1130, 28)
foot("Actual local AI draft, reviewed and confirmed in the browser. Synthetic inputs and funds.")

slide("Emergency access separates withdrawal and payment.")
img = ImageReader(str(ROOT / "reports/emergency.png"))
c.drawImage(img, 68, 148, width=725, height=389, preserveAspectRatio=True, anchor="c")
text("PHP 600 withdrawn\nPHP 20 left in buffer\n\nOptional PHP 75/week\nfor an estimated 8 weeks", 836, 213, 375, 27)
foot("Actual mock-wallet screen. Withdrawal works after analysis revocation. No refill debit is scheduled.")

slide("The tests pass. Impact still needs evidence.")
table([["Base synthetic comparison", "No saving", "Fixed 10%", "Ipon"],
       ["Fully funded shocks / 281", "88", "95", "95"],
       ["Essential shortfall days", "1,437", "1,206", "1,248"],
       ["Median buffer days", "0.00", "1.33", "1.27"]], 68, 195, [490, 240, 205, 205], 63)
text("Ipon has more shortfall days than fixed 10% saving here.\nSavings can suppress discretionary spending in this model.", 68, 477, 1135, 27)
foot("148 backend + 4 frontend tests passed. 90 invented households over 180 days. No measured impact.")

slide("AI helps draft. Deterministic rules decide.")
text("Text entry and proposed fields", 68, 207, 555, 31, GREEN, True)
text("qwen3:1.7b via local Ollama\nEvidence checks clear uncertain fields\nUser review and confirmation", 68, 284, 555, 27)
text("Confirmed plan and transfers", 674, 207, 545, 31, GREEN, True)
text("Exact centavo arithmetic\nFresh recommendation and consent\nAtomic transfer with retry protection", 674, 284, 535, 27)
text("Raw model: 8/40 strict cases passed before added checks.\nWith checks: 11/12 new examples matched; 1 asked for a date.\nDifferent samples and review rules; reliability remains unproven.", 68, 485, 1140, 26)
foot("Codex review, not independent validation. Raw outputs and replay retained. No live financial integration.")

slide("A partner-paid service is the business hypothesis.")
table([["Placeholder monthly economics", "PHP"],
       ["Partner fee per active user", "20"],
       ["Variable cost, including AI compute", "8"],
       ["Contribution per active user", "12"],
       ["Fixed operating cost", "120,000"]], 68, 195, [560, 140], 64)
text("10,000", 838, 227, 350, 62, GREEN, True)
text("active users at operating\nbreak-even under these\nassumptions", 838, 332, 355, 27)
foot("No user fee in the concept. No contracted partner. PHP 300,000 one-time integration excluded above.")

slide("A 90-day pilot would test comprehension and access.")
phases = [("Days 1-30", "8-10 exploratory interviews\nIntegration and risk review"),
          ("Days 31-60", "Shadow recommendations\nNo money movement"),
          ("Days 61-90", "Limited opt-in pilot if approved\nMeasure access and shortfalls")]
for i, (title, detail) in enumerate(phases):
    text(title, 68+i*396, 220, 350, 34, GREEN, True)
    text(detail, 68+i*396, 310, 350, 27)
text("Manual versus AI plan entry: compare confirmed-field errors,\ntime, corrections and understanding of the review step.", 68, 518, 1130, 28)
foot("Proposed research. Agree sample size, thresholds, comparison and stop rules before launch.")

slide("Seeking a Philippine discovery and pilot partner.", True)
text("A wallet or financial-services partner\nand access to prospective irregular-income users.", 68, 220, 1140, 40, "#FFFFFF")
text("Next: validate the planning experience, improve AI reliability,\nand define a controlled integration pilot.", 68, 423, 1120, 30, "#DFE9D5")
text("APPLICANT REVIEW REQUIRED\nTeam identity, background and contact details have not been supplied.", 68, 588, 1120, 23, "#DFE9D5")
c.save()
print(f"Created {OUT}: {page} slides")
