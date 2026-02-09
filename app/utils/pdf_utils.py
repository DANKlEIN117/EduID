from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from io import BytesIO
import os
from datetime import datetime, timedelta


def generate_id_pdf(student_data, id_number, qr_code_path, photo_path=None, filename=None, school_config=None):
    """
    Generate a professional two-sided school ID card as PDF
    Front: Photo, Name, ID, QR Code, Class
    Back: Emergency Info, Barcode, School Motto, Validity Date
    
    Args:
        student_data: Dict with student info (full_name, reg_no, class_level, blood_type, allergies, emergency_contact_name, emergency_contact_phone)
        id_number: School ID number
        qr_code_path: Path to QR code image
        photo_path: Path to student photo (optional)
        filename: Path to save PDF (if None, returns BytesIO object)
        school_config: Dict with school branding (name, motto, color)
    
    Returns:
        Path to saved PDF or BytesIO object
    """
    try:
        # ID card dimensions (standard: 85.6 x 53.98 mm or 3.37 x 2.13 inches)
        id_width = 3.5 * inch
        id_height = 2.2 * inch
        
        if school_config is None:
            school_config = {
                'name': 'School ID',
                'motto': 'Excellence in Education',
                'color': '#1a5490'
            }
        
        # Always use BytesIO first, then save to file if needed
        buffer = BytesIO()
        
        # Create PDF with single page showing both sides (front on top, back on bottom)
        page_width = 8.5 * inch  # Standard letter width
        page_height = 11 * inch   # Standard letter height
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=(page_width, page_height),
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        school_header_style = ParagraphStyle(
            'SchoolHeader',
            parent=styles['Heading1'],
            fontSize=10,
            textColor=colors.HexColor('#ffffff'),
            spaceAfter=2,
            alignment=1,
            fontName='Helvetica-Bold'
        )
        
        name_style = ParagraphStyle(
            'CardName',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.HexColor(school_config.get('color', '#1a5490')),
            spaceAfter=1,
            alignment=1,
            fontName='Helvetica-Bold'
        )
        
        label_style = ParagraphStyle(
            'CardLabel',
            parent=styles['Normal'],
            fontSize=5.5,
            textColor=colors.HexColor('#777777'),
            spaceAfter=0,
            alignment=1,
            fontName='Helvetica'
        )
        
        value_style = ParagraphStyle(
            'CardValue',
            parent=styles['Normal'],
            fontSize=6.5,
            textColor=colors.HexColor('#000000'),
            spaceAfter=0,
            alignment=1,
            fontName='Helvetica-Bold'
        )
        
        school_style = ParagraphStyle(
            'SchoolName',
            parent=styles['Normal'],
            fontSize=6.5,
            textColor=colors.HexColor(school_config.get('color', '#1a5490')),
            spaceAfter=0,
            alignment=1,
            fontName='Helvetica-Bold'
        )
        
        # ============ FRONT SIDE ============
        front_data = []
        
        # Row 1: School Header (colored background with school name)
        front_data.append([Paragraph(school_config.get('name', 'SCHOOL'), school_header_style)])
        
        # Row 2: Spacer
        front_data.append([Spacer(1, 0.05*inch)])
        
        # Row 3: Photo
        if photo_path and os.path.exists(photo_path):
            try:
                photo = Image(photo_path, width=0.7*inch, height=0.85*inch)
                front_data.append([photo])
            except:
                front_data.append([Paragraph("[Photo]", label_style)])
        else:
            front_data.append([Paragraph("[Photo]", label_style)])
        
        # Row 4: Student Name (stylized)
        front_data.append([Spacer(1, 0.03*inch)])
        front_data.append([Paragraph(f"<b>{student_data.get('full_name', 'N/A').upper()}</b>", name_style)])
        
        # Row 5: ID Number (prominent)
        front_data.append([Spacer(1, 0.02*inch)])
        id_display_style = ParagraphStyle('IDDisplay', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor(school_config.get('color', '#1a5490')), spaceAfter=0, alignment=1, fontName='Helvetica-Bold')
        front_data.append([Paragraph(f"{id_number}", id_display_style)])
        front_data.append([Paragraph("STUDENT ID", label_style)])
        
        # Row 6: Class/Level (if provided)
        if student_data.get('class_level'):
            front_data.append([Spacer(1, 0.02*inch)])
            front_data.append([Paragraph(f"{student_data.get('class_level')}", value_style)])
            front_data.append([Paragraph("CLASS", label_style)])
        
        # Row 7: QR Code
        if qr_code_path and os.path.exists(qr_code_path):
            try:
                front_data.append([Spacer(1, 0.03*inch)])
                qr = Image(qr_code_path, width=0.5*inch, height=0.5*inch)
                front_data.append([qr])
            except:
                pass
        
        # Create front table with colored header
        front_table = Table(front_data, colWidths=[3.2*inch])
        front_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(school_config.get('color', '#1a5490'))),  # Header background
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),  # Card background
            ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor(school_config.get('color', '#1a5490'))),
            ('TOPPADDING', (0, 0), (0, 0), 3),  # More padding for header
            ('BOTTOMPADDING', (0, 0), (0, 0), 3),
        ]))
        
        story.append(front_table)
        story.append(Spacer(0.15*inch, 0))  # Spacing between front and back
        
        # ============ BACK SIDE ============
        back_data = []
        
        # Row 1: School Header (colored background)
        back_data.append([Paragraph(school_config.get('name', 'SCHOOL'), school_header_style)])
        
        # Row 2: School Motto
        back_data.append([Spacer(1, 0.02*inch)])
        back_data.append([Paragraph(f"<i>{school_config.get('motto', '')}</i>", ParagraphStyle('Motto', parent=styles['Normal'], fontSize=5.5, alignment=1, textColor=colors.HexColor('#666666')))])
        
        # Row 3: Emergency Header
        back_data.append([Spacer(1, 0.04*inch)])
        back_data.append([Paragraph("<b>⚠️ EMERGENCY INFO</b>", ParagraphStyle('EmergHeader', parent=styles['Normal'], fontSize=6, alignment=1, textColor=colors.HexColor('#d00000'), fontName='Helvetica-Bold'))])
        
        # Row 4: Blood Type & Allergies
        blood_text = ""
        if student_data.get('blood_type'):
            blood_text += f"<b>Blood:</b> {student_data.get('blood_type')}"
        if student_data.get('allergies'):
            if blood_text:
                blood_text += " | "
            blood_text += f"<b>Allergies:</b> {student_data.get('allergies')}"
        
        if blood_text:
            back_data.append([Paragraph(blood_text, ParagraphStyle('EmergInfo', parent=styles['Normal'], fontSize=4.5, alignment=1))])
        
        # Row 5: Emergency Contact
        if student_data.get('emergency_contact_name'):
            emerg_text = f"<b>Contact:</b> {student_data.get('emergency_contact_name')}"
            if student_data.get('emergency_contact_phone'):
                emerg_text += f" | {student_data.get('emergency_contact_phone')}"
            back_data.append([Paragraph(emerg_text, ParagraphStyle('EmergContact', parent=styles['Normal'], fontSize=4.5, alignment=1))])
        
        # Row 6: Validity/Expiry
        expiry_date = (datetime.utcnow() + timedelta(days=365)).strftime('%m/%d/%Y')
        back_data.append([Spacer(1, 0.02*inch)])
        back_data.append([Paragraph(f"<b>Valid Until:</b> {expiry_date}", ParagraphStyle('Validity', parent=styles['Normal'], fontSize=5, alignment=1, textColor=colors.HexColor('#333333')))])
        
        # Row 7: ID Barcode representation
        back_data.append([Spacer(1, 0.01*inch)])
        back_data.append([Paragraph(f"║ {student_data.get('reg_no', 'ID')} ║", ParagraphStyle('Barcode', parent=styles['Normal'], fontSize=5.5, alignment=1, fontName='Courier'))])
        
        # Row 8: Digital ID Info
        back_data.append([Paragraph("📱 Digital ID", ParagraphStyle('Digital', parent=styles['Normal'], fontSize=5, alignment=1, textColor=colors.HexColor('#0066cc')))])
        
        # Create back table with colored header
        back_table = Table(back_data, colWidths=[3.2*inch])
        back_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(school_config.get('color', '#1a5490'))),  # Header background
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),  # Card background
            ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor(school_config.get('color', '#1a5490'))),
            ('TOPPADDING', (0, 0), (0, 0), 3),  # More padding for header
            ('BOTTOMPADDING', (0, 0), (0, 0), 3),
        ]))
        
        # Create a vertical layout with front and back stacked
        try:
            # Center align the front and back cards
            story.append(Spacer(1, 0.3*inch))
            
            # Add front table centered
            front_centered = Table([[front_table]], colWidths=[id_width])
            front_centered.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(front_centered)
            
            # Add spacing between front and back
            story.append(Spacer(1, 0.3*inch))
            
            # Add back table centered
            back_centered = Table([[back_table]], colWidths=[id_width])
            back_centered.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(back_centered)
            
        except Exception as table_error:
            print(f"Error creating centered layout: {table_error}")
            # Fallback: add tables directly
            story.append(Spacer(1, 0.3*inch))
            story.append(front_table)
            story.append(Spacer(1, 0.3*inch))
            story.append(back_table)
        
        # Build PDF
        try:
            doc.build(story)
        except Exception as build_error:
            print(f"Error building PDF document: {build_error}")
            raise build_error
        
        # If filename provided, save BytesIO to file
        if filename:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            buffer.seek(0)
            with open(filename, 'wb') as f:
                f.write(buffer.getvalue())
            buffer.close()
            return filename
        else:
            buffer.seek(0)
            return buffer
            
    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_bulk_print_pdf(id_records, qr_code_paths, photo_paths=None, school_config=None):
    """
    Generate a multi-page PDF for bulk printing IDs in vertical list format on A4 pages
    
    Args:
        id_records: List of student data dicts with (id, full_name, reg_no, class_level, blood_type, allergies, emergency_contact_name, emergency_contact_phone)
        qr_code_paths: Dict mapping student_id to QR code path
        photo_paths: Dict mapping student_id to photo path (optional)
        school_config: Dict with school branding (name, motto, color)
    
    Returns:
        BytesIO object with PDF
    """
    try:
        buffer = BytesIO()
        
        if school_config is None:
            school_config = {
                'name': 'School ID',
                'motto': 'Excellence in Education',
                'color': '#1a5490'
            }
        
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
        
        # Add title
        title_style = ParagraphStyle(
            'BulkTitle',
            parent=styles['Heading1'],
            fontSize=14,
            alignment=1,
            textColor=colors.HexColor(school_config.get('color', '#1a5490')),
            fontName='Helvetica-Bold',
            spaceAfter=12
        )
        story.append(Paragraph(f"Bulk Print - {school_config.get('name', 'School ID')}", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Add each student's ID record
        for idx, student in enumerate(id_records):
            try:
                student_id = student.get('id')
                qr_path = qr_code_paths.get(student_id)
                photo_path = photo_paths.get(student_id) if photo_paths else None
                
                # Create a simple record for each student
                record_data = []
                
                # School name header
                record_data.append([Paragraph(school_config.get('name', 'SCHOOL'), 
                    ParagraphStyle('RecordSchool', parent=styles['Normal'], fontSize=9, 
                    alignment=1, textColor=colors.HexColor(school_config.get('color', '#1a5490')), 
                    fontName='Helvetica-Bold'))])
                
                # Student info
                record_data.append([Paragraph(f"<b>{student.get('full_name', 'N/A')}</b>", 
                    ParagraphStyle('RecordName', parent=styles['Normal'], fontSize=10, 
                    alignment=1, fontName='Helvetica-Bold'))])
                
                record_data.append([Paragraph(f"Reg: {student.get('reg_no', 'N/A')} | ID: {student.get('id')}", 
                    ParagraphStyle('RecordID', parent=styles['Normal'], fontSize=8, alignment=1))])
                
                # Class and school name
                class_text = f"Class: {student.get('class_level', 'N/A')}"
                if student.get('school_name'):
                    class_text += f" | {student.get('school_name')}"
                record_data.append([Paragraph(class_text, 
                    ParagraphStyle('RecordClass', parent=styles['Normal'], fontSize=8, alignment=1))])
                
                # Emergency info summary
                if student.get('blood_type') or student.get('allergies'):
                    emerg_text = f"<b>Emergency:</b> "
                    if student.get('blood_type'):
                        emerg_text += f"Blood {student.get('blood_type')}"
                    if student.get('allergies'):
                        if student.get('blood_type'):
                            emerg_text += " | "
                        emerg_text += f"Allergies: {student.get('allergies')}"
                    record_data.append([Paragraph(emerg_text, 
                        ParagraphStyle('RecordEmerg', parent=styles['Normal'], fontSize=7, alignment=1))])
                
                # Create record table
                record_table = Table(record_data, colWidths=[7*inch])
                record_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9f9f9')),
                    ('BORDER', (0, 0), (-1, -1), 0.5, colors.HexColor(school_config.get('color', '#1a5490'))),
                ]))
                
                story.append(record_table)
                story.append(Spacer(1, 0.2*inch))
                
            except Exception as student_error:
                print(f"Error processing student {idx}: {student_error}")
                continue
        
        # Build PDF
        try:
            doc.build(story)
            buffer.seek(0)
            return buffer
        except Exception as build_error:
            print(f"Error building bulk PDF: {build_error}")
            raise build_error
        
    except Exception as e:
        print(f"Error generating bulk PDF: {e}")
        import traceback
        traceback.print_exc()
        return None
