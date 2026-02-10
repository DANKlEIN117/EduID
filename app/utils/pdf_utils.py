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

        # Top: Institution logo (if provided) and name centered
        logo_path = None
        if school_config and school_config.get('logo_path') and os.path.exists(school_config.get('logo_path')):
            logo_path = school_config.get('logo_path')

        if logo_path:
            try:
                logo = Image(logo_path, width=1.2*inch, height=0.6*inch)
                front_data.append([logo, Paragraph(school_config.get('name', 'SCHOOL'), school_header_style)])
            except:
                front_data.append([Paragraph(school_config.get('name', 'SCHOOL'), school_header_style)])
        else:
            front_data.append([Paragraph(school_config.get('name', 'SCHOOL'), school_header_style)])

        # Spacer
        front_data.append([Spacer(1, 0.04*inch)])

        # Main row: Photo (left) and main details (right)
        # Photo
        if photo_path and os.path.exists(photo_path):
            try:
                photo = Image(photo_path, width=1.0*inch, height=1.2*inch)
            except:
                photo = Paragraph('[Photo]', label_style)
        else:
            photo = Paragraph('[Photo]', label_style)

        # Details on right
        details = []
        details.append(Paragraph(f"<b>{student_data.get('full_name', 'N/A')}</b>", ParagraphStyle('NameRight', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=0)))
        details.append(Paragraph(f"ID: {id_number}", ParagraphStyle('IDRight', parent=styles['Normal'], fontSize=8, alignment=0, textColor=colors.HexColor('#000000'))))
        # Course / Program
        course = student_data.get('course') or student_data.get('program') or student_data.get('class_level') or ''
        if course:
            details.append(Paragraph(f"{course}", ParagraphStyle('Course', parent=styles['Normal'], fontSize=8, alignment=0)))
        # Year of study
        year = student_data.get('year') or student_data.get('year_of_study') or ''
        if year:
            details.append(Paragraph(f"Year: {year}", ParagraphStyle('Year', parent=styles['Normal'], fontSize=8, alignment=0)))
        # Validity
        if student_data.get('valid_until'):
            validity_text = student_data.get('valid_until')
        else:
            validity_text = (datetime.utcnow() + timedelta(days=365)).strftime('%b %Y')
        details.append(Paragraph(f"Valid Until: {validity_text}", ParagraphStyle('Valid', parent=styles['Normal'], fontSize=8, alignment=0, textColor=colors.HexColor('#333333'))))

        right_col = Table([[d] for d in details], colWidths=[2.1*inch])
        right_col.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))

        # Combine photo and right details
        front_main = Table([[photo, right_col]], colWidths=[1.2*inch, 2.1*inch])
        front_main.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))

        # Add the main composite to front_data
        front_data.append([front_main])
        
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
        
        # Row 7: Barcode / QR and emergency & utility info
        # Left: QR/barcode
        left_back = None
        if qr_code_path and os.path.exists(qr_code_path):
            try:
                left_back = Image(qr_code_path, width=1.0*inch, height=1.0*inch)
            except:
                left_back = Paragraph('QR', label_style)
        else:
            left_back = Paragraph('QR', label_style)

        # Right: emergency contact, library instructions, address & website
        back_right_parts = []
        # Emergency contact
        if student_data.get('emergency_contact_name') or student_data.get('emergency_contact_phone'):
            contact = student_data.get('emergency_contact_name', '')
            if student_data.get('emergency_contact_phone'):
                contact += f" ({student_data.get('emergency_contact_phone')})"
            back_right_parts.append(Paragraph(f"<b>Emergency:</b> {contact}", ParagraphStyle('BackEmerg', parent=styles['Normal'], fontSize=8, alignment=0, textColor=colors.HexColor('#d00000'))))

        # Library / Access instructions
        back_right_parts.append(Paragraph("<b>Access Instructions:</b> Scan at entry points", ParagraphStyle('BackAccess', parent=styles['Normal'], fontSize=7.5, alignment=0)))

        # Address & website from school_config
        address = school_config.get('address') if school_config else None
        website = school_config.get('website') if school_config else None
        addr_lines = ''
        if address:
            addr_lines += address
        if website:
            if addr_lines:
                addr_lines += ' | '
            addr_lines += website
        if addr_lines:
            back_right_parts.append(Paragraph(addr_lines, ParagraphStyle('BackAddr', parent=styles['Normal'], fontSize=7, alignment=0, textColor=colors.HexColor('#333333'))))

        right_back = Table([[p] for p in back_right_parts], colWidths=[2.1*inch])
        right_back.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))

        back_main = Table([[left_back, right_back]], colWidths=[1.2*inch, 2.1*inch])
        back_main.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))

        back_data.append([back_main])
        
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
        
        # Add each student's ID record (build compact cards)
        cards = []
        for idx, student in enumerate(id_records):
            try:
                student_id = student.get('id')
                qr_path = qr_code_paths.get(student_id)
                photo_path = photo_paths.get(student_id) if photo_paths else None
                
                # Build a two-column layout: photo (left) and details + QR (right)
                # Left: photo
                if photo_path and os.path.exists(photo_path):
                    try:
                        left_cell = Image(photo_path, width=1.1*inch, height=1.25*inch)
                    except:
                        left_cell = Paragraph("[Photo]", ParagraphStyle('RecordPhotoPlaceholder', parent=styles['Normal'], fontSize=8, alignment=1))
                else:
                    left_cell = Paragraph("[Photo]", ParagraphStyle('RecordPhotoPlaceholder', parent=styles['Normal'], fontSize=8, alignment=1))

                # Right: details
                right_cells = []
                # Institution name (small)
                if school_config.get('name'):
                    right_cells.append([Paragraph(school_config.get('name'), ParagraphStyle('RecordSchoolSmall', parent=styles['Normal'], fontSize=9, alignment=0, textColor=colors.HexColor(school_config.get('color', '#1a5490')), fontName='Helvetica-Bold'))])
                # Student name and ID
                right_cells.append([Paragraph(f"<b>{student.get('full_name', 'N/A')}</b>", ParagraphStyle('RecordName', parent=styles['Normal'], fontSize=11, alignment=0, fontName='Helvetica-Bold'))])
                right_cells.append([Paragraph(f"ID: {student.get('id')} | Reg: {student.get('reg_no', 'N/A')}", ParagraphStyle('RecordReg', parent=styles['Normal'], fontSize=9, alignment=0))])

                # Course / Program and Year
                course_text = student.get('course') or student.get('class_level') or ''
                if course_text:
                    right_cells.append([Paragraph(course_text, ParagraphStyle('RecordCourse', parent=styles['Normal'], fontSize=8, alignment=0))])
                if student.get('year'):
                    right_cells.append([Paragraph(f"Year: {student.get('year')}", ParagraphStyle('RecordYear', parent=styles['Normal'], fontSize=8, alignment=0))])

                # Validity
                if student.get('valid_until'):
                    right_cells.append([Paragraph(f"Valid Until: {student.get('valid_until')}", ParagraphStyle('RecordValid', parent=styles['Normal'], fontSize=8, alignment=0))])

                # Emergency info
                if student.get('blood_type') or student.get('allergies') or student.get('emergency_contact_name'):
                    emerg_parts = []
                    if student.get('blood_type'):
                        emerg_parts.append(f"Blood: {student.get('blood_type')}")
                    if student.get('allergies') and student.get('allergies') != 'None':
                        emerg_parts.append(f"Allergies: {student.get('allergies')}")
                    if student.get('emergency_contact_name'):
                        contact = student.get('emergency_contact_name')
                        if student.get('emergency_contact_phone'):
                            contact += f" ({student.get('emergency_contact_phone')})"
                        emerg_parts.append(f"Contact: {contact}")
                    right_cells.append([Paragraph(" | ".join(emerg_parts), ParagraphStyle('RecordEmerg', parent=styles['Normal'], fontSize=8, alignment=0, textColor=colors.HexColor('#d00000')))])

                # Access / library instructions
                right_cells.append([Paragraph("Access: Scan at entry points", ParagraphStyle('RecordAccess', parent=styles['Normal'], fontSize=7.5, alignment=0))])

                # Address & website
                addr = school_config.get('address') or ''
                web = school_config.get('website') or ''
                addrline = ' | '.join([x for x in [addr, web] if x])
                if addrline:
                    right_cells.append([Paragraph(addrline, ParagraphStyle('RecordAddr', parent=styles['Normal'], fontSize=7, alignment=0, textColor=colors.HexColor('#333333')))])

                # QR image (placed last)
                qr_flowable = None
                if qr_path and os.path.exists(qr_path):
                    try:
                        qr_flowable = Image(qr_path, width=0.9*inch, height=0.9*inch)
                        right_cells.append([Spacer(1, 0.02*inch)])
                        right_cells.append([qr_flowable])
                    except:
                        pass

                # Assemble right inner table (single column with multiple rows)
                # compact right column for card width
                right_inner = Table(right_cells, colWidths=[2.3*inch])
                right_inner.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                # compact record card
                card_width = 3.2 * inch
                record_table = Table([[left_cell, right_inner]], colWidths=[1.0*inch, 2.2*inch])
                record_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor(school_config.get('color', '#1a5490'))),
                ]))

                cards.append(record_table)
                
            except Exception as student_error:
                print(f"Error processing student {idx}: {student_error}")
                continue
        
        # Arrange cards two-up per row and paginate
        id_card_width = 3.2 * inch
        rows_per_page = 4  # with card height ~2.4" we can fit ~4 rows per page
        row_count = 0

        for i in range(0, len(cards), 2):
            left = cards[i]
            right = cards[i+1] if i+1 < len(cards) else Spacer(id_card_width, 0)

            pair = Table([[left, right]], colWidths=[id_card_width, id_card_width])
            pair.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))

            story.append(pair)
            story.append(Spacer(1, 0.15*inch))
            row_count += 1

            if row_count >= rows_per_page:
                story.append(PageBreak())
                row_count = 0

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
