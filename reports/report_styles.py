import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    Table, TableStyle, Paragraph, Spacer, Image,
    BaseDocTemplate, PageTemplate, Frame, Flowable
)
from reportlab.platypus.flowables import HRFlowable

# ----------------------------------------------------------------------
# University Branding
# ----------------------------------------------------------------------
UNIVERSITY_NAME_LINE1 = "THE BENAZIR BHUTTO SHAHEED UNIVERSITY"
UNIVERSITY_NAME_LINE2 = "OF TECHNOLOGY & SKILLS DEVELOPMENT"
UNIVERSITY_LOCATION = "Khairpur Mirs"
SYSTEM_NAME = "Transport Management System"
LOGO_PATH = os.path.join("resources", "images", "logo.png")

PRIMARY_BROWN = HexColor("#6B3B21")
ACCENT_BROWN = HexColor("#AB6038")
TABLE_HEADER_BG = PRIMARY_BROWN
TABLE_HEADER_FG = white
ROW_ALT = HexColor("#FDF6E3")
ROW_NORM = white
BORDER_COLOR = PRIMARY_BROWN
SUMMARY_BG = HexColor("#F9F2E7")
SUMMARY_TITLE_BG = PRIMARY_BROWN
SUMMARY_TITLE_FG = white

# Page dimensions and layout
PAGE_W, PAGE_H = A4
MARGIN_LEFT = 18 * mm
MARGIN_RIGHT = 18 * mm
MARGIN_TOP = 25 * mm     # top space before header
MARGIN_BOTTOM = 20 * mm  # bottom space after footer

# Header height will be computed dynamically based on content
HEADER_GAP = 15 * mm     # space between header bottom and body start

# ----------------------------------------------------------------------
# Typography Styles
# ----------------------------------------------------------------------
styles = getSampleStyleSheet()

# University name lines (inside the header table)
uni_line1_style = ParagraphStyle(
    "UniLine1",
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=18,
    textColor=PRIMARY_BROWN,
    alignment=TA_LEFT,
)
uni_line2_style = ParagraphStyle(
    "UniLine2",
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=18,
    textColor=PRIMARY_BROWN,
    alignment=TA_LEFT,
)
uni_loc_style = ParagraphStyle(
    "UniLoc",
    fontName="Helvetica",
    fontSize=10,
    leading=13,
    textColor=ACCENT_BROWN,
    alignment=TA_LEFT,
)
uni_system_style = ParagraphStyle(
    "SysName",
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
    textColor=PRIMARY_BROWN,
    alignment=TA_LEFT,
)

# Report title (e.g., "VEHICLE LOG REPORT")
report_title_style = ParagraphStyle(
    "ReportTitle",
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
    textColor=PRIMARY_BROWN,
    alignment=TA_CENTER,
    spaceAfter=8 * mm,
)

# Section headings inside reports
section_heading_style = ParagraphStyle(
    "SectionHeading",
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
    textColor=PRIMARY_BROWN,
    spaceBefore=6 * mm,
    spaceAfter=3 * mm,
)

# Information panel labels & values
info_label_style = ParagraphStyle(
    "InfoLabel",
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=12,
    textColor=PRIMARY_BROWN,
    alignment=TA_LEFT,
)

info_value_style = ParagraphStyle(
    "InfoValue",
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=black,
    alignment=TA_LEFT,
)

# Table header & body
table_header_style = ParagraphStyle(
    "TableHeader",
    fontName="Helvetica-Bold",
    fontSize=8.5,
    leading=11,
    textColor=TABLE_HEADER_FG,
    alignment=TA_CENTER,
)

table_body_style = ParagraphStyle(
    "TableBody",
    fontName="Helvetica",
    fontSize=8.5,
    leading=11,
    textColor=black,
    alignment=TA_CENTER,
)

# Summary box
summary_title_style = ParagraphStyle(
    "SummaryTitle",
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=16,
    textColor=SUMMARY_TITLE_FG,
    alignment=TA_CENTER,
)

summary_label_style = ParagraphStyle(
    "SummaryLabel",
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=12,
    textColor=PRIMARY_BROWN,
    alignment=TA_LEFT,
)

summary_value_style = ParagraphStyle(
    "SummaryValue",
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=black,
    alignment=TA_LEFT,
)

# Footer (used in canvas)
footer_style = ParagraphStyle(
    "Footer",
    fontName="Helvetica",
    fontSize=8,
    leading=10,
    textColor=HexColor("#4B4B4B"),
    alignment=TA_CENTER,
)

# ----------------------------------------------------------------------
# Reusable Components
# ----------------------------------------------------------------------

def get_logo(width=24*mm, height=24*mm):
    """Return an Image flowable if the logo exists, else a transparent spacer."""
    if os.path.exists(LOGO_PATH):
        img = Image(LOGO_PATH, width=width, height=height)
        img.hAlign = 'LEFT'
        return img
    else:
        # return a blank placeholder with same dimensions to maintain alignment
        return Spacer(width, height)


def build_header_table():
    """
    Build the university header as a ReportLab Table.
    Left column: logo (24x24 mm). Right column: university name block.
    Returns the Table flowable.
    """
    logo_img = get_logo(24*mm, 24*mm)

    # University name block as a nested table of paragraphs
    name_lines = [
        [Paragraph(UNIVERSITY_NAME_LINE1, uni_line1_style)],
        [Paragraph(UNIVERSITY_NAME_LINE2, uni_line2_style)],
        [Paragraph(UNIVERSITY_LOCATION, uni_loc_style)],
        [Paragraph(SYSTEM_NAME, uni_system_style)]
    ]
    name_block = Table(name_lines, colWidths=[None])
    name_block.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 4*mm),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    header_data = [[logo_img, name_block]]
    header_table = Table(header_data, colWidths=[26*mm, None])
    header_table.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'LEFT'),
    ]))
    return header_table


def compute_header_height():
    """Return the height of the header table after wrapping to the page width."""
    header_table = build_header_table()
    available_width = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    w, h = header_table.wrap(available_width, PAGE_H)
    return h


def draw_page_decorations(canvas, doc, user_name=""):
    """
    Canvas callback that draws the header table at the top of every page
    and the footer at the bottom, without manual coordinate tweaking.
    """
    canvas.saveState()
    # --- Header ---
    header_table = build_header_table()
    header_height = compute_header_height()
    available_width = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    header_table.wrap(available_width, header_height)
    # Position the header table: x = MARGIN_LEFT, y = PAGE_H - MARGIN_TOP + something?
    # We want top of header at MARGIN_TOP from top edge.
    header_table.drawOn(canvas, MARGIN_LEFT, PAGE_H - MARGIN_TOP - header_height)

    # Separator line below header
    canvas.setStrokeColor(PRIMARY_BROWN)
    canvas.setLineWidth(2)
    line_y = PAGE_H - MARGIN_TOP - header_height - 4 * mm
    canvas.line(MARGIN_LEFT, line_y, PAGE_W - MARGIN_RIGHT, line_y)

    # --- Footer ---
    footer_y = MARGIN_BOTTOM
    canvas.setStrokeColor(ACCENT_BROWN)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_LEFT, footer_y + 8*mm, PAGE_W - MARGIN_RIGHT, footer_y + 8*mm)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(HexColor("#4B4B4B"))
    # Left: system name and date
    left_str = f"BBSUTSD Transport Management System | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    canvas.drawString(MARGIN_LEFT, footer_y + 3*mm, left_str)
    # Center: generated by
    if user_name:
        canvas.drawCentredString(PAGE_W / 2, footer_y + 3*mm, f"Generated by: {user_name}")
    # Right: page number
    canvas.drawRightString(PAGE_W - MARGIN_RIGHT, footer_y + 3*mm,
                           f"Page {canvas.getPageNumber()}")

    canvas.restoreState()


# ----------------------------------------------------------------------
# Information Panel
# ----------------------------------------------------------------------
def build_info_panel(info_dict: dict, title="Vehicle Information"):
    """
    Creates a bordered information panel with brown title bar.
    info_dict: ordered dict of label -> value.
    Returns a Table flowable.
    """
    data = [[Paragraph(title, summary_title_style)]]
    for label, value in info_dict.items():
        data.append([
            Paragraph(str(label), info_label_style),
            Paragraph(str(value), info_value_style)
        ])
    # Use 40% / 60% of available width (which will be set later by the report)
    col_widths = [None, None]  # will be auto-sized; we'll set fixed widths later
    t = Table(data, colWidths=col_widths, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('SPAN', (0,0), (-1,0)),
        ('BACKGROUND', (0,0), (-1,0), SUMMARY_TITLE_BG),
        ('TEXTCOLOR', (0,0), (-1,0), SUMMARY_TITLE_FG),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,1), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,0), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,1), (-1,-1), SUMMARY_BG),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t


# ----------------------------------------------------------------------
# Data Table Builder
# ----------------------------------------------------------------------
def build_data_table(headers: list, data: list, col_widths=None):
    """
    Build a full-width data table with brown header and alternating row colors.
    col_widths: optional list of column widths; if None, equally divide available width.
    """
    header_paragraphs = [Paragraph(h, table_header_style) for h in headers]
    rows = [[Paragraph(str(cell), table_body_style) for cell in row] for row in data]
    full_data = [header_paragraphs] + rows

    t = Table(full_data, colWidths=col_widths, hAlign='LEFT', repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('TEXTCOLOR', (0,0), (-1,0), TABLE_HEADER_FG),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (0,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [ROW_NORM, ROW_ALT]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    return t


# ----------------------------------------------------------------------
# Summary Box
# ----------------------------------------------------------------------
def build_summary_box(summary_items: list, title="Summary"):
    """
    Creates a bordered summary box with brown title bar and beige background.
    summary_items: list of (label, value) tuples.
    Returns a Table flowable.
    """
    data = [[Paragraph(title, summary_title_style)]]
    for label, value in summary_items:
        data.append([
            Paragraph(str(label), summary_label_style),
            Paragraph(str(value), summary_value_style)
        ])
    t = Table(data, colWidths=[None, None], hAlign='LEFT')
    t.setStyle(TableStyle([
        ('SPAN', (0,0), (-1,0)),
        ('BACKGROUND', (0,0), (-1,0), SUMMARY_TITLE_BG),
        ('TEXTCOLOR', (0,0), (-1,0), SUMMARY_TITLE_FG),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,1), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,0), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,1), (-1,-1), SUMMARY_BG),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t


# ----------------------------------------------------------------------
# Spacers and Separators
# ----------------------------------------------------------------------
def spacer(height=5*mm):
    return Spacer(1, height)


def horizontal_line():
    return HRFlowable(width="100%", thickness=1, color=ACCENT_BROWN)


# ----------------------------------------------------------------------
# Page Template Factory
# ----------------------------------------------------------------------
class ReportDocTemplate(BaseDocTemplate):
    """
    Custom document template that uses a frame starting below the header
    and draws the header table on every page.
    """
    def __init__(self, filename, user_name="", **kwargs):
        super().__init__(filename, **kwargs)
        self.user_name = user_name
        # Compute header height once
        self.header_height = compute_header_height()
        # Body frame: starts after header + gap, ends before footer area
        frame_top = PAGE_H - MARGIN_TOP - self.header_height - HEADER_GAP
        frame_bottom = MARGIN_BOTTOM + 12 * mm  # leave room for footer line
        frame = Frame(
            MARGIN_LEFT, frame_bottom,
            PAGE_W - MARGIN_LEFT - MARGIN_RIGHT,
            frame_top - frame_bottom,
            id='main'
        )
        template = PageTemplate(id='Main', frames=[frame],
                                onPage=self._on_page)
        self.addPageTemplates([template])

    def _on_page(self, canvas, doc):
        draw_page_decorations(canvas, doc, self.user_name)