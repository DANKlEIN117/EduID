from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from io import BytesIO
import os
from datetime import datetime


def generate_id_pdf(student_data, id_number, qr_code_path, photo_path=None, filename=None):
    """
    Generate a school ID as PDF
    
    Args:
        student_data: Dict with student info (full_name, reg_no, class_level, etc)
        id_number: School ID number
        qr_code_path: Path to QR code image
        photo_path: Path to student photo (optional)
        filename: Path to save PDF (if None, returns BytesIO object)
    
    Returns:
        Path to saved PDF or BytesIO object
    """
    try:
        # ID card dimensions (standard ID card: 85.6 x 53.98 mm or 3.37 x 2.13 inches)
        id_width = 3.5 * inch
        id_height = 2.2 * inch
        
        if filename:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            buffer = open(filename, 'wb')
        else:
            buffer = BytesIO()
        
        # Create PDF with custom page size for ID card
        doc = SimpleDocTemplate(
            buffer,
            pagesize=(id_width, id_height),
            rightMargin=0.1*inch,
            leftMargin=0.1*inch,
            topMargin=0.1*inch,
            bottomMargin=0.1*inch
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=2,
            alignment=1,  # center
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#333333'),
            spaceAfter=1,
            alignment=1
        )
        
        # Build content
        content_data = []
        
        # Top section - School name
        content_data.append([Paragraph("STUDENT ID CARD", title_style)])
        content_data.append([Spacer(1, 0.05*inch)])
        
        # Photo and QR section
        photo_qr_data = []
        
        if photo_path and os.path.exists(photo_path):
            try:
                photo = Image(photo_path, width=0.8*inch, height=1*inch)
                photo_qr_data.append(photo)
            except:
                pass
        
        if qr_code_path and os.path.exists(qr_code_path):
            try:
                qr = Image(qr_code_path, width=0.7*inch, height=0.7*inch)
                photo_qr_data.append(Spacer(0.1*inch, 0))
                photo_qr_data.append(qr)
            except:
                pass
        
        if photo_qr_data:
            content_data.append([Table([photo_qr_data], colWidths=[1.6*inch])])
        
        content_data.append([Spacer(1, 0.05*inch)])
        
        # Student info
        full_name = student_data.get('full_name', 'N/A')
        reg_no = student_data.get('reg_no', 'N/A')
        id_num = student_data.get('id_number', id_number)
        class_level = student_data.get('class_level', 'N/A')
        
        content_data.append([Paragraph(f"<b>{full_name}</b>", normal_style)])
        content_data.append([Paragraph(f"Reg No: {reg_no}", normal_style)])
        content_data.append([Paragraph(f"ID: {id_num}", normal_style)])
        content_data.append([Paragraph(f"Class: {class_level}", normal_style)])
        
        # Build table
        table = Table(content_data, colWidths=[id_width - 0.2*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        story.append(table)
        
        # Build PDF
        doc.build(story)
        
        if filename:
            buffer.close()
            return filename
        else:
            buffer.seek(0)
            return buffer
            
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None


def generate_bulk_print_pdf(id_records, qr_code_paths, photo_paths=None):
    """
    Generate a multi-page PDF for printing multiple IDs
    
    Args:
        id_records: List of student data dicts
        qr_code_paths: Dict mapping student_id to QR code path
        photo_paths: Dict mapping student_id to photo path (optional)
    
    Returns:
        BytesIO object with PDF
    """
    try:
        buffer = BytesIO()
        
        # Use A4 for printing
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # ID dimensions for multi-page printing
        id_width = 3.5 * inch
        id_height = 2.2 * inch
        
        # Add each ID to the PDF
        for idx, student in enumerate(id_records):
            student_id = student.get('id')
            qr_path = qr_code_paths.get(student_id)
            photo_path = photo_paths.get(student_id) if photo_paths else None
            
            # Generate ID content and add to story
            # This is a simplified version - you can enhance it
            story.append(Paragraph(f"<b>{student.get('full_name', 'N/A')}</b>", styles['Heading3']))
            story.append(Paragraph(f"Reg No: {student.get('reg_no', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Add page break between IDs if not the last one
            if idx < len(id_records) - 1:
                story.append(PageBreak())
        
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Error generating bulk PDF: {e}")
        return None
