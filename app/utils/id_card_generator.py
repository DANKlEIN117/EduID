from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os

# PVC card (credit card) physical size: 85.6mm x 54mm
CARD_W_MM = 85.6
CARD_H_MM = 54
BLEED_MM = 3  # 3mm bleed standard

# Convert to points (ReportLab uses points; 1 mm = 2.835 pts)
MM_TO_PT = mm

CARD_W_PT = CARD_W_MM * MM_TO_PT
CARD_H_PT = CARD_H_MM * MM_TO_PT
BLEED_PT = BLEED_MM * MM_TO_PT

PAGE_W = CARD_W_PT + 2 * BLEED_PT
PAGE_H = CARD_H_PT + 2 * BLEED_PT


def generate_pvc_id_pdf(student, school_config=None, photo_path=None, qr_data=None, filename=None):
    """
    Generate a two-page PDF (FRONT and BACK) sized for PVC printing with 3mm bleed.

    Args:
        student: dict with keys: full_name, id_number, reg_no, course, year, valid_until, emergency_contact, address
        school_config: dict with keys: name, color (hex), logo_path, website
        photo_path: path to passport photo image
        qr_data: string or URL to encode in QR on the back
        filename: path to save PDF. If None returns BytesIO

    Output:
        BytesIO or saved file (PDF) with two pages: front then back.
    """
    if school_config is None:
        school_config = {
            'name': 'SCHOOL NAME',
            'color': '#0b5394',
            'logo_path': None,
            'website': ''
        }

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_W, PAGE_H))

    def draw_card_background():
        # draw bleed area background (white) then inner rounded rect for card
        c.setFillColor(colors.white)
        c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

        # card area origin
        ox = BLEED_PT
        oy = BLEED_PT
        # rounded rect backdrop (light)
        c.setFillColor(colors.HexColor('#ffffff'))
        c.setStrokeColor(colors.HexColor(school_config.get('color')))
        c.setLineWidth(0.8)
        r = 6  # corner radius in points
        # background panel
        c.roundRect(ox, oy, CARD_W_PT, CARD_H_PT, r, stroke=0, fill=1)

    # ---------- FRONT ----------
    draw_card_background()

    ox = BLEED_PT
    oy = BLEED_PT

    # padding inside card
    pad = 6 * mm

    # Logo (top-left or centered top)
    logo_w = 22 * mm
    logo_h = 9 * mm
    if school_config.get('logo_path') and os.path.exists(school_config.get('logo_path')):
        try:
            logo = ImageReader(school_config.get('logo_path'))
            c.drawImage(logo, ox + pad, oy + CARD_H_PT - pad - logo_h, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    else:
        # Draw school name centered top
        c.setFont('Helvetica-Bold', 9)
        c.setFillColor(colors.HexColor(school_config.get('color')))
        c.drawCentredString(ox + CARD_W_PT / 2, oy + CARD_H_PT - pad - 6, school_config.get('name'))

    # Photo area (left)
    photo_w = 24 * mm
    photo_h = 30 * mm
    photo_x = ox + pad
    photo_y = oy + CARD_H_PT - pad - logo_h - 8*mm - photo_h
    # ensure photo_y not negative
    if photo_y < oy + pad:
        photo_y = oy + pad

    if photo_path and os.path.exists(photo_path):
        try:
            img = ImageReader(photo_path)
            c.drawImage(img, photo_x, photo_y, width=photo_w, height=photo_h, mask='auto')
            # frame with rounded corners (visual)
            c.setStrokeColor(colors.HexColor(school_config.get('color')))
            c.setLineWidth(0.8)
            c.roundRect(photo_x - 1, photo_y - 1, photo_w + 2, photo_h + 2, 4, stroke=1, fill=0)
        except Exception:
            c.setFillColor(colors.lightgrey)
            c.rect(photo_x, photo_y, photo_w, photo_h, stroke=0, fill=1)
    else:
        # placeholder box
        c.setFillColor(colors.lightgrey)
        c.rect(photo_x, photo_y, photo_w, photo_h, stroke=0, fill=1)
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 6)
        c.drawCentredString(photo_x + photo_w/2, photo_y + photo_h/2, 'Photo')

    # Right side text block (name, id, course, year, valid)
    tx = photo_x + photo_w + 6*mm
    ty_top = photo_y + photo_h

    # Full name
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(colors.black)
    c.drawString(tx, ty_top - 2, student.get('full_name', '').strip())

    # ID / Admission
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#333333'))
    c.drawString(tx, ty_top - 16, f"ID: {student.get('id_number') or student.get('reg_no','')}")

    # Course / program
    if student.get('course'):
        c.drawString(tx, ty_top - 30, student.get('course'))

    # Year
    if student.get('year'):
        c.drawString(tx, ty_top - 44, f"Year: {student.get('year')}")

    # Validity (bottom-right)
    c.setFont('Helvetica', 7)
    c.setFillColor(colors.HexColor('#333333'))
    c.drawRightString(ox + CARD_W_PT - pad, oy + pad + 6, f"Valid Until: {student.get('valid_until','')}")

    # subtle divider line near bottom
    c.setStrokeColor(colors.HexColor('#e6e6e6'))
    c.setLineWidth(0.5)
    c.line(ox + pad, oy + 18, ox + CARD_W_PT - pad, oy + 18)

    # small school website under divider
    if school_config.get('website'):
        c.setFont('Helvetica', 6.5)
        c.setFillColor(colors.HexColor('#666666'))
        c.drawCentredString(ox + CARD_W_PT/2, oy + 8, school_config.get('website'))

    c.showPage()

    # ---------- BACK ----------
    draw_card_background()

    # QR / Barcode (left or center-left)
    qr_size = 28 * mm
    qr_x = ox + pad
    qr_y = oy + CARD_H_PT/2 - qr_size/2

    if qr_data:
        try:
            qr_code = qr.QrCodeWidget(qr_data)
            bounds = qr_code.getBounds()
            w = bounds[2] - bounds[0]
            h = bounds[3] - bounds[1]
            d = Drawing(qr_size, qr_size)
            d.add(qr_code)
            renderPDF.draw(d, c, qr_x, qr_y)
        except Exception:
            c.setFillColor(colors.lightgrey)
            c.rect(qr_x, qr_y, qr_size, qr_size, stroke=0, fill=1)
    else:
        c.setFillColor(colors.lightgrey)
        c.rect(qr_x, qr_y, qr_size, qr_size, stroke=0, fill=1)

    # Right side: emergency contact, address, usage rules
    bx = qr_x + qr_size + 6*mm
    by = qr_y + qr_size

    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(colors.HexColor('#000000'))
    c.drawString(bx, by - 2, 'Emergency Contact:')
    c.setFont('Helvetica', 8)
    c.drawString(bx, by - 16, student.get('emergency_contact_name', '') or school_config.get('contact',''))
    c.drawString(bx, by - 30, student.get('emergency_contact_phone','') or school_config.get('contact_phone',''))

    # Address
    addr_y = by - 48
    c.setFont('Helvetica-Bold', 7.5)
    c.drawString(bx, addr_y, 'Address:')
    c.setFont('Helvetica', 7)
    addr = student.get('address') or school_config.get('address') or ''
    text_obj = c.beginText()
    text_obj.setTextOrigin(bx, addr_y - 12)
    text_obj.setFont('Helvetica', 7)
    for line in addr.split('\n')[:3]:
        text_obj.textLine(line)
    c.drawText(text_obj)

    # Usage rules and property note
    usage_y = oy + 18
    c.setFont('Helvetica', 6.5)
    c.setFillColor(colors.HexColor('#333333'))
    c.drawString(ox + pad, usage_y, 'Property of the school • Report lost cards immediately')

    # Signature strip (optional)
    strip_w = 40 * mm
    strip_h = 8 * mm
    sx = ox + CARD_W_PT - pad - strip_w
    sy = oy + pad
    c.setStrokeColor(colors.HexColor('#999999'))
    c.setLineWidth(0.4)
    c.rect(sx, sy, strip_w, strip_h, stroke=1, fill=0)
    c.setFont('Helvetica', 6)
    c.drawCentredString(sx + strip_w/2, sy + 2, 'Signature')

    c.showPage()

    if filename:
        # ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        c.save()
        buffer.seek(0)
        with open(filename, 'wb') as f:
            f.write(buffer.getvalue())
        buffer.close()
        return filename
    else:
        c.save()
        buffer.seek(0)
        return buffer
