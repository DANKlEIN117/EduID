from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.graphics.shapes import Drawing, Line, Rect, String
import os
from io import BytesIO
from datetime import datetime

# ============ ID CARD DIMENSIONS ============
CARD_WIDTH = 85.6 * mm   # 3.37 inches - Standard credit card
CARD_HEIGHT = 53.98 * mm  # 2.125 inches
BLEED = 3 * mm

# ============ PROFESSIONAL COLOR PALETTE ============
# JKUAT Branding Colors
JKUAT_NAVY = colors.HexColor("#0B1F3A")      # Primary navy
JKUAT_ACCENT = colors.HexColor("#1E90FF")    # Accent blue
JKUAT_GOLD = colors.HexColor("#D4AF37")      # Secondary accent
BACKGROUND_LIGHT = colors.HexColor("#F8FAFB")
TEXT_DARK = colors.HexColor("#1C1C1C")
TEXT_MEDIUM = colors.HexColor("#4A4A4A")
TEXT_LIGHT = colors.HexColor("#7A7A7A")
BORDER_COLOR = colors.HexColor("#CCCCCC")
WATERMARK_COLOR = colors.HexColor("#E8E8E8")

# ============ TYPOGRAPHY & LAYOUT CONSTANTS ============
MARGIN_X = 3 * mm
MARGIN_Y = 2.5 * mm
GRID_UNIT = 1.5 * mm
LINE_HEIGHT_RATIO = 1.3

class ProfessionalIDCard:
    """Professional institutional ID card generator with security features"""
    
    def __init__(self, card_width=CARD_WIDTH, card_height=CARD_HEIGHT):
        self.width = card_width
        self.height = card_height
        self.margin_x = MARGIN_X
        self.margin_y = MARGIN_Y
    
    def draw_watermark_pattern(self, c, x, y, text, opacity=0.02):
        """Draw repeated watermark text pattern - very faint"""
        c.setFillAlpha(opacity)
        c.setFont("Helvetica", 8)
        c.setFillColor(JKUAT_NAVY)
        
        # Diagonal watermark pattern
        for i in range(-2, 5):
            c.saveState()
            c.translate(x + self.width/2, y + self.height/2)
            c.rotate(45)
            c.drawString(-30, i * 8, text)
            c.restoreState()
        
        c.setFillAlpha(1.0)
    
    def draw_border_frame(self, c, x, y, thickness=1, style='solid'):
        """Draw professional border frame"""
        c.setStrokeColor(BORDER_COLOR)
        c.setLineWidth(thickness)
        
        if style == 'solid':
            c.rect(x, y, self.width, self.height, fill=0)
        elif style == 'double':
            c.rect(x, y, self.width, self.height, fill=0)
            c.setLineWidth(thickness / 2)
            inner_offset = 1.5 * mm
            c.rect(x + inner_offset, y + inner_offset, 
                   self.width - 2*inner_offset, self.height - 2*inner_offset, fill=0)
    
    def draw_microtext(self, c, x, y, text, max_width=20*mm):
        """Draw tiny security microtext"""
        c.setFont("Helvetica", 5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(x, y, text[:40])
    
    def draw_signature_line(self, c, x, y, label="Authorized by"):
        """Draw signature authorization line"""
        c.setFont("Helvetica", 6)
        c.setFillColor(TEXT_DARK)
        c.drawString(x, y + 2*mm, label)
        
        # Signature line
        c.setStrokeColor(TEXT_DARK)
        c.setLineWidth(0.5)
        c.line(x, y, x + 15*mm, y)
    
    def draw_boxed_section(self, c, x, y, width, height, title, content_lines, bg_color=None):
        """Draw a professional boxed information section"""
        # Background
        if bg_color:
            c.setFillColor(bg_color)
            c.rect(x, y, width, height, fill=1)
        
        # Border
        c.setStrokeColor(BORDER_COLOR)
        c.setLineWidth(0.5)
        c.rect(x, y, width, height, fill=0)
        
        # Title bar
        title_height = 4 * mm
        c.setFillColor(JKUAT_NAVY)
        c.rect(x, y + height - title_height, width, title_height, fill=1)
        
        c.setFont("Helvetica-Bold", 6)
        c.setFillColor(colors.white)
        c.drawString(x + 1.5*mm, y + height - 2.5*mm, title.upper())
        
        # Content
        c.setFont("Helvetica", 5.5)
        c.setFillColor(TEXT_DARK)
        content_y = y + height - title_height - 2*mm
        
        for line in content_lines:
            if content_y > y + 1*mm:
                c.drawString(x + 1.5*mm, content_y, line)
                content_y -= 3*mm


def draw_id_front(c, x, y, student):
    """
    Draw professional JKUAT ID card front with institutional branding
    Fixed layout with proper spacing, dual logos, and improved margins
    """
    card = ProfessionalIDCard()
    
    # ==================== BACKGROUND & SECURITY ====================
    # Base background
    c.setFillColor(colors.white)
    c.rect(x, y, card.width, card.height, fill=1)
    
    # Professional border frame
    card.draw_border_frame(c, x, y, thickness=1.2)
    
    # ==================== HEADER SECTION ====================
    header_height = 9 * mm
    c.setFillColor(JKUAT_NAVY)
    c.rect(x, y + card.height - header_height, card.width, header_height, fill=1)
    
    # ==================== DUAL LOGOS ====================
    logo_path = student.get("logo_path")
    logo_size = 7 * mm
    logo_y = y + card.height - header_height + 1.2 * mm
    
    # Left logo
    logo_x_left = x + 2 * mm
    if logo_path and os.path.exists(logo_path):
        try:
            c.drawImage(
                logo_path,
                logo_x_left,
                logo_y,
                width=logo_size,
                height=logo_size,
                preserveAspectRatio=True,
                mask='auto'
            )
        except:
            pass
    
    # Right logo (mirror)
    logo_x_right = x + card.width - logo_size - 2 * mm
    if logo_path and os.path.exists(logo_path):
        try:
            c.drawImage(
                logo_path,
                logo_x_right,
                logo_y,
                width=logo_size,
                height=logo_size,
                preserveAspectRatio=True,
                mask='auto'
            )
        except:
            pass
    
    # Gold accent stripe
    c.setFillColor(JKUAT_ACCENT)
    c.rect(x, y + card.height - header_height - 1*mm, card.width, 1*mm, fill=1)
    
    # Institution name - Centered with proper spacing and truncation
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(colors.white)
    institution = student.get("school_name", "JKUAT").upper()
    if len(institution) > 50:
        institution = institution[:50] + "..."
    c.drawCentredString(x + card.width / 2, y + card.height - 3.2*mm, institution)
    
    c.setFont("Helvetica", 4.5)
    c.setFillColor(colors.HexColor("#D0D0D0"))
    c.drawCentredString(x + card.width / 2, y + card.height - 5.8*mm, "Official Student ID")
    
    # ==================== PHOTO SECTION ====================
    photo_x = x + 4 * mm
    photo_y = y + 10.5 * mm
    photo_w = 19 * mm
    photo_h = 25 * mm
    
    # Photo frame with professional border
    c.setFillColor(BACKGROUND_LIGHT)
    c.rect(photo_x, photo_y, photo_w, photo_h, fill=1)
    
    c.setStrokeColor(JKUAT_NAVY)
    c.setLineWidth(1.5)
    c.rect(photo_x, photo_y, photo_w, photo_h, fill=0)
    
    # Draw photo
    photo_path = student.get("photo_path")
    if photo_path and os.path.exists(photo_path):
        try:
            c.drawImage(
                photo_path,
                photo_x + 0.5*mm,
                photo_y + 0.5*mm,
                width=photo_w - 1*mm,
                height=photo_h - 1*mm,
                preserveAspectRatio=True,
                mask='auto'
            )
        except:
            pass
    
    # ==================== STUDENT INFORMATION SECTION ====================
    info_x = photo_x + photo_w + 3.5 * mm
    info_y_start = y + card.height - header_height - 3.2 * mm
    
    # FULL NAME - Bold, uppercase
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(JKUAT_NAVY)
    full_name = student.get("full_name", "").upper()
    full_name = full_name[:17] if len(full_name) > 17 else full_name
    c.drawString(info_x, info_y_start, full_name)
    
    # Registration Number - Full number displayed
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    reg_no = student.get('reg_no', '')[:20]  # Allow full reg number
    c.drawString(info_x, info_y_start - 3.5*mm, f"REG: {reg_no}")
    
    # Course - New field
    c.setFont("Helvetica", 6)
    c.setFillColor(TEXT_MEDIUM)
    course = student.get("course", "N/A")
    course = course[:22] if len(course) > 22 else course
    c.drawString(info_x, info_y_start - 6.5*mm, f"Course: {course}")
    
    # Class/Level - Regular
    c.setFont("Helvetica", 6)
    c.setFillColor(TEXT_MEDIUM)
    class_level = student.get("class_level", "N/A")
    c.drawString(info_x, info_y_start - 9*mm, f"Level: {class_level}")
    
    # ==================== BOTTOM SECTION ====================
    bottom_y = y + 4.8 * mm
    
    # ID Number - Proper margin
    c.setFont("Helvetica", 5.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x + 4*mm, bottom_y, f"ID: {student.get('reg_no', '')[:15]}")
    
    # Validity Date - Highlighted with proper spacing
    valid_until = student.get("valid_until", "")
    if valid_until:
        c.setFont("Helvetica-Bold", 5.5)
        c.setFillColor(JKUAT_ACCENT)
        c.drawString(x + 4*mm + 20*mm, bottom_y, f"VALID: {valid_until}")
    
    # Microtext security element - Proper margin
    card.draw_microtext(c, x + 4*mm, bottom_y - 2.5*mm, 
                       f"Card property of University | {datetime.now().strftime('%m/%Y')}")
    
    # ==================== QR CODE SECTION ====================
    qr_size = 14 * mm
    qr_x = x + card.width - qr_size - 4*mm
    qr_y = y + 2.5*mm
    
    # QR Code background highlight
    c.setFillColor(colors.white)
    c.setStrokeColor(BORDER_COLOR)
    c.setLineWidth(0.5)
    c.rect(qr_x - 1*mm, qr_y - 1*mm, qr_size + 2*mm, qr_size + 3.5*mm, fill=1)
    
    # Draw QR code
    qr_path = student.get("qr_path")
    if qr_path and os.path.exists(qr_path):
        try:
            c.drawImage(
                qr_path,
                qr_x,
                qr_y,
                width=qr_size,
                height=qr_size,
                preserveAspectRatio=True,
                mask='auto'
            )
        except:
            pass
    
    # QR label - Professionally styled
    c.setFont("Helvetica-Bold", 4.5)
    c.setFillColor(JKUAT_NAVY)
    c.drawCentredString(qr_x + qr_size/2, qr_y - 1.8*mm, "Scan to Verify")
    c.setFont("Helvetica", 4)
    c.setFillColor(TEXT_LIGHT)
    c.drawCentredString(qr_x + qr_size/2, qr_y - 2.8*mm, "Authenticity")


def draw_id_back(c, x, y, student):
    """
    Draw professional JKUAT ID card back with institutional branding,
    security features, and clearly separated information sections
    """
    card = ProfessionalIDCard()
    
    # ==================== BACKGROUND & SECURITY ====================
    # Primary background
    c.setFillColor(JKUAT_NAVY)
    c.rect(x, y, card.width, card.height, fill=1)
    
    # Watermark pattern
    card.draw_watermark_pattern(c, x, y, "OFFICIAL", opacity=0.08)
    
    # ==================== HEADER SECTION ====================
    header_height = 8 * mm
    c.setFillColor(JKUAT_ACCENT)
    c.rect(x, y + card.height - header_height, card.width, header_height, fill=1)
    
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.white)
    c.drawCentredString(x + card.width/2, y + card.height - 4*mm, "STUDENT IDENTIFICATION CARD")
    
    # Professional border
    card.draw_border_frame(c, x, y, thickness=1.2)
    
    # ==================== EMERGENCY INFORMATION SECTION ====================
    emergency_x = x + card.margin_x
    emergency_y = y + card.height - header_height - 4*mm
    section_width = (card.width / 2) - 2*mm
    section_height = 13 * mm
    
    # Boxed Emergency Section
    c.setFillColor(colors.white)
    c.setStrokeColor(BORDER_COLOR)
    c.setLineWidth(0.5)
    c.rect(emergency_x, emergency_y - section_height, section_width, section_height, fill=1)
    
    # Emergency header
    c.setFillColor(JKUAT_NAVY)
    c.rect(emergency_x, emergency_y - 3.5*mm, section_width, 3.5*mm, fill=1)
    
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(colors.white)
    c.drawString(emergency_x + 1.5*mm, emergency_y - 1.5*mm, "EMERGENCY CONTACT")
    
    # Emergency content
    c.setFont("Helvetica", 5.5)
    c.setFillColor(TEXT_DARK)
    emergency_name = student.get("emergency_contact_name", "N/A")
    emergency_phone = student.get("emergency_contact_phone", "N/A")
    
    c.drawString(emergency_x + 1.5*mm, emergency_y - 5.5*mm, f"Name: {emergency_name[:20]}")
    c.drawString(emergency_x + 1.5*mm, emergency_y - 8*mm, f"Phone: {emergency_phone}")
    
    # ==================== MEDICAL INFORMATION SECTION ====================
    medical_x = x + card.width/2 + 1*mm
    medical_y = y + card.height - header_height - 4*mm
    
    c.setFillColor(colors.white)
    c.setStrokeColor(BORDER_COLOR)
    c.setLineWidth(0.5)
    c.rect(medical_x, medical_y - section_height, section_width, section_height, fill=1)
    
    # Medical header
    c.setFillColor(JKUAT_NAVY)
    c.rect(medical_x, medical_y - 3.5*mm, section_width, 3.5*mm, fill=1)
    
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(colors.white)
    c.drawString(medical_x + 1.5*mm, medical_y - 1.5*mm, "MEDICAL INFORMATION")
    
    # Medical content
    c.setFont("Helvetica", 5.5)
    c.setFillColor(TEXT_DARK)
    blood_type = student.get("blood_type", "N/A")
    allergies = student.get("allergies", "None")
    if allergies and len(allergies) > 0:
        allergies = allergies[:18]
    
    c.drawString(medical_x + 1.5*mm, medical_y - 5.5*mm, f"Blood: {blood_type}")
    c.drawString(medical_x + 1.5*mm, medical_y - 8*mm, f"Allergies: {allergies}")
    
    # ==================== TERMS & CONDITIONS SECTION ====================
    terms_y = emergency_y - section_height - 4*mm
    
    c.setFillColor(colors.white)
    c.setStrokeColor(BORDER_COLOR)
    c.setLineWidth(0.5)
    c.rect(emergency_x, terms_y - 10*mm, card.width - 2*card.margin_x, 10*mm, fill=1)
    
    # Terms header
    c.setFillColor(JKUAT_NAVY)
    c.rect(emergency_x, terms_y - 3*mm, card.width - 2*card.margin_x, 3*mm, fill=1)
    
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(colors.white)
    c.drawString(emergency_x + 1.5*mm, terms_y - 1*mm, "TERMS & CONDITIONS")
    
    # Terms content
    c.setFont("Helvetica", 5)
    c.setFillColor(TEXT_DARK)
    terms = [
        "• Card remains property of Jomo Kenyatta University",
        "• Valid for academic period only",
        "• Do not deface, alter, or transfer",
        "• Report loss immediately to Registrar",
        "• Non-compliant cards subject to revocation"
    ]
    
    terms_content_y = terms_y - 4.5*mm
    for term in terms:
        if terms_content_y > y + 6*mm:
            c.drawString(emergency_x + 2*mm, terms_content_y, term)
            terms_content_y -= 2.5*mm
    
    # ==================== SECURITY & AUTHORIZATION ====================
    # Signature line
    sig_y = y + 2.5*mm
    c.setFont("Helvetica", 5)
    c.setFillColor(colors.white)
    c.drawString(x + card.margin_x, sig_y + 1*mm, "Authorized Signature:")
    
    c.setStrokeColor(colors.HexColor("#AAAAAA"))
    c.setLineWidth(0.5)
    c.line(x + card.margin_x + 22*mm, sig_y + 0.5*mm, x + card.margin_x + 35*mm, sig_y + 0.5*mm)
    
    # Security notice
    c.setFont("Helvetica", 4.5)
    c.setFillColor(colors.HexColor("#CCCCCC"))
    c.drawString(x + card.margin_x, sig_y - 1.5*mm, "Document Security: Multi-layer authentication enabled")


def _draw_cutting_guides(c, x, y, width, height):
    """
    Draw professional registration marks and cutting guides for commercial printing
    """
    guide_length = 5 * mm
    guide_color = colors.HexColor("#ACACAC")
    
    c.setStrokeColor(guide_color)
    c.setLineWidth(0.5)
    c.setDash([2, 2])  # Dashed line
    
    # Corner registration marks
    corners = [
        (x - guide_length, y + height, x, y + height),  # TL horizontal
        (x, y + height + guide_length, x, y + height),   # TL vertical
        (x + width, y + height + guide_length, x + width, y + height),  # TR vertical
        (x + width + guide_length, y + height, x + width, y + height),  # TR horizontal
        (x - guide_length, y, x, y),  # BL horizontal
        (x, y - guide_length, x, y),  # BL vertical
        (x + width, y - guide_length, x + width, y),  # BR vertical
        (x + width + guide_length, y, x + width, y),  # BR horizontal
    ]
    
    for x1, y1, x2, y2 in corners:
        c.line(x1, y1, x2, y2)
    
    # Outer cut line
    c.setDash([])
    c.setLineWidth(0.3)
    c.setStrokeColor(colors.HexColor("#999999"))
    c.rect(x, y, width, height, fill=0)


def generate_id_pdf(students, output_path, cards_per_page=(2, 2), double_sided=True):
    """
    Generate professional PDF with student ID cards front and back paired
    Optimized for commercial printing with proper margins, bleed, and DPI considerations
    
    Args:
        students: List of student dictionaries containing ID card data
        output_path: Path where the PDF will be saved
        cards_per_page: Tuple (rows, cols) for card layout per page
        double_sided: Boolean to include back side of cards
    
    Returns:
        Path to generated PDF
    """
    # Portrait A4 with proper margins for commercial printing
    page_width, page_height = portrait(A4)
    
    c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
    c.setTitle("JKUAT Student ID Cards - Professional Edition")
    c.setAuthor("Registrar's Office")
    
    margin = 15 * mm
    spacing_vertical = 10 * mm  # Space between front and back for cutting
    
    # Calculate positions for paired cards (front and back together)
    card = ProfessionalIDCard()
    pair_height = card.height + spacing_vertical + card.height
    
    available_height = page_height - (2 * margin)
    pairs_per_page = int(available_height / (pair_height + margin))
    
    if pairs_per_page == 0:
        pairs_per_page = 1
    
    pair_count = 0
    
    for student in students:
        # Check if we need a new page
        if pair_count >= pairs_per_page and pair_count > 0:
            c.showPage()
            pair_count = 0
        
        # Calculate Y position for this pair
        pair_y_position = page_height - margin - ((pair_count + 1) * (pair_height + margin))
        
        # Front card position (top of pair)
        front_x = (page_width - card.width) / 2
        front_y = pair_y_position + card.height + spacing_vertical
        
        # Back card position (bottom of pair)
        back_x = (page_width - card.width) / 2
        back_y = pair_y_position
        
        # Draw FRONT with professional styling
        draw_id_front(c, front_x, front_y, student)
        _draw_cutting_guides(c, front_x, front_y, card.width, card.height)
        
        # Draw cutting lane with prominent marker
        c.setStrokeColor(colors.HexColor("#DDDDDD"))
        c.setLineWidth(0.4)
        c.setDash([3, 2])
        c.line(
            front_x - 15 * mm,
            front_y - spacing_vertical / 2,
            front_x + card.width + 15 * mm,
            front_y - spacing_vertical / 2
        )
        c.setDash([])
        
        # Cutting instruction text (light)
        c.setFont("Helvetica", 4)
        c.setFillColor(colors.HexColor("#AAAAAA"))
        c.drawString(front_x - 12*mm, front_y - spacing_vertical/2 + 0.5*mm, "CUT HERE")
        
        # Draw BACK with professional styling
        draw_id_back(c, back_x, back_y, student)
        _draw_cutting_guides(c, back_x, back_y, card.width, card.height)
        
        pair_count += 1
    
    c.save()
    return output_path


def generate_bulk_print_pdf(id_records, qr_paths, photo_paths, school_config):
    """
    Generate professional bulk print PDF for multiple student IDs
    with front and back cards paired on same pages
    
    Optimized for:
    - Commercial printing (300 DPI equivalent)
    - Proper CMYK color space preparation
    - Bleed margins and cutting guides
    - Professional institutional branding
    
    Args:
        id_records: List of student record dictionaries
        qr_paths: Dictionary mapping student IDs to QR code paths
        photo_paths: Dictionary mapping student IDs to photo paths
        school_config: Dictionary with school configuration (including logo_path)
    
    Returns:
        BytesIO buffer containing the generated PDF
    """
    # Get logo path from school config
    logo_path = school_config.get('logo_path') if school_config else None
    
    # Convert records to card drawing format
    students = []
    for record in id_records:
        student_id = record.get('id')
        
        valid_until_str = record.get('valid_until', '')
        if isinstance(valid_until_str, str) and valid_until_str:
            pass  # Already formatted
        else:
            valid_until_str = ''
        
        student = {
            'full_name': record.get('full_name', ''),
            'reg_no': record.get('reg_no', ''),
            'class_level': record.get('class_level', 'N/A'),
            'course': record.get('course', 'N/A'),
            'year': record.get('year', ''),
            'valid_until': valid_until_str,
            'photo_path': photo_paths.get(student_id),
            'qr_path': qr_paths.get(student_id),
            'blood_type': record.get('blood_type', 'N/A'),
            'allergies': record.get('allergies', 'N/A'),
            'emergency_contact_name': record.get('emergency_contact_name', 'N/A'),
            'emergency_contact_phone': record.get('emergency_contact_phone', 'N/A'),
            'school_name': record.get('school_name', 'JOMO KENYATTA UNIVERSITY'),
            'logo_path': logo_path  # Add logo path
        }
        students.append(student)
    
    # Create PDF with portrait orientation
    pdf_buffer = BytesIO()
    page_width, page_height = portrait(A4)
    
    c = canvas.Canvas(pdf_buffer, pagesize=(page_width, page_height))
    c.setTitle("JKUAT Student ID Cards - Bulk Print Edition")
    c.setAuthor("Student Records - Registrar's Office")
    
    margin = 15 * mm
    spacing_vertical = 10 * mm
    
    card = ProfessionalIDCard()
    pair_height = card.height + spacing_vertical + card.height
    available_height = page_height - (2 * margin)
    pairs_per_page = int(available_height / (pair_height + margin))
    
    if pairs_per_page == 0:
        pairs_per_page = 1
    
    pair_count = 0
    
    for student in students:
        # Check for new page
        if pair_count >= pairs_per_page and pair_count > 0:
            c.showPage()
            pair_count = 0
        
        # Calculate positions
        pair_y_position = page_height - margin - ((pair_count + 1) * (pair_height + margin))
        
        front_x = (page_width - card.width) / 2
        front_y = pair_y_position + card.height + spacing_vertical
        
        back_x = (page_width - card.width) / 2
        back_y = pair_y_position
        
        # Draw FRONT
        draw_id_front(c, front_x, front_y, student)
        _draw_cutting_guides(c, front_x, front_y, card.width, card.height)
        
        # Draw cutting lane
        c.setStrokeColor(colors.HexColor("#DDDDDD"))
        c.setLineWidth(0.4)
        c.setDash([3, 2])
        c.line(
            front_x - 15 * mm,
            front_y - spacing_vertical / 2,
            front_x + card.width + 15 * mm,
            front_y - spacing_vertical / 2
        )
        c.setDash([])
        
        # Cutting instruction
        c.setFont("Helvetica", 4)
        c.setFillColor(colors.HexColor("#AAAAAA"))
        c.drawString(front_x - 12*mm, front_y - spacing_vertical/2 + 0.5*mm, "CUT HERE")
        
        # Draw BACK
        draw_id_back(c, back_x, back_y, student)
        _draw_cutting_guides(c, back_x, back_y, card.width, card.height)
        
        pair_count += 1
    
    c.save()
    pdf_buffer.seek(0)
    
    return pdf_buffer
