from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
import os
import secrets
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.student import Student, SchoolID
from app.forms import StudentProfileForm, IDSubmissionForm
from app.decorators import student_required
from app.utils.qr_utils import generate_qr_code
from app.utils.pdf_utils import generate_id_pdf
from datetime import datetime

student_bp = Blueprint("student", __name__, url_prefix="/student")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@student_bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    student = Student.query.filter_by(user_id=current_user.id).first()
    school_ids = []
    if student:
        school_ids = SchoolID.query.filter_by(student_id=student.id).order_by(SchoolID.submission_date.desc()).all()
    
    return render_template("student/dashboard.html", student=student, school_ids=school_ids)


@student_bp.route("/profile", methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if not student:
        flash('Student profile not found', 'danger')
        return redirect(url_for('student.dashboard'))
    
    form = StudentProfileForm()
    
    if form.validate_on_submit():
        student.reg_no = form.reg_no.data
        student.full_name = form.full_name.data
        student.school_name = form.school_name.data
        student.course = form.course.data
        student.email = form.email.data
        student.phone = form.phone.data
        student.class_level = form.class_level.data
        student.blood_type = form.blood_type.data
        student.allergies = form.allergies.data
        student.emergency_contact_name = form.emergency_contact_name.data
        student.emergency_contact_phone = form.emergency_contact_phone.data
        
        if form.date_of_birth.data:
            try:
                student.date_of_birth = datetime.strptime(form.date_of_birth.data, '%Y-%m-%d').date()
            except:
                pass
        
        if form.valid_until.data:
            try:
                student.valid_until = datetime.strptime(form.valid_until.data, '%Y-%m-%d').date()
            except:
                pass
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('student.profile'))
    
    elif request.method == 'GET':
        form.reg_no.data = student.reg_no
        form.full_name.data = student.full_name
        form.school_name.data = student.school_name
        form.course.data = student.course
        form.email.data = student.email
        form.phone.data = student.phone
        form.class_level.data = student.class_level
        form.blood_type.data = student.blood_type
        form.allergies.data = student.allergies
        form.emergency_contact_name.data = student.emergency_contact_name
        form.emergency_contact_phone.data = student.emergency_contact_phone
        if student.date_of_birth:
            form.date_of_birth.data = student.date_of_birth.strftime('%Y-%m-%d')
        if student.valid_until:
            form.valid_until.data = student.valid_until.strftime('%Y-%m-%d')
    
    return render_template("student/profile.html", form=form, student=student)


@student_bp.route("/submit-id", methods=['GET', 'POST'])
@login_required
@student_required
def submit_id():
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if not student:
        flash('Student profile not found', 'danger')
        return redirect(url_for('student.dashboard'))
    
    form = IDSubmissionForm()
    
    if form.validate_on_submit():
        try:
            # Check if student already has a pending submission
            pending = SchoolID.query.filter_by(student_id=student.id, status='pending').first()
            if pending:
                flash('You already have a pending ID submission. Please wait for admin review.', 'warning')
                return redirect(url_for('student.dashboard'))
            
            # Generate unique ID number
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            id_number = f"SID{student.reg_no}{timestamp}"
            
            # Create uploads directory
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Handle photo upload
            photo_path = None
            if form.photo.data:
                file = form.photo.data
                filename = secure_filename(file.filename)
                filename = f"{student.id}_{secrets.token_hex(8)}_{filename}"
                photo_path = os.path.join(UPLOAD_FOLDER, 'photos', filename)
                os.makedirs(os.path.dirname(photo_path), exist_ok=True)
                file.save(photo_path)
                # Store relative path
                photo_path = os.path.relpath(photo_path, current_app.root_path)
            
            # Generate QR code
            qr_path = os.path.join(UPLOAD_FOLDER, 'qr_codes', f"{student.id}_{id_number}.png")
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)
            generate_qr_code(id_number, qr_path)
            qr_path = os.path.relpath(qr_path, current_app.root_path)
            
            # Create SchoolID record
            school_id = SchoolID(
                student_id=student.id,
                id_number=id_number,
                status='pending',
                qr_code=qr_path,
                preview_image=photo_path,
                notes=form.notes.data
            )
            
            db.session.add(school_id)
            db.session.commit()
            
            flash('ID submitted successfully! Admin will review your submission.', 'success')
            return redirect(url_for('student.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting ID: {str(e)}', 'danger')
    
    return render_template("student/submit_id.html", form=form, student=student)


@student_bp.route("/id/<int:id_id>/preview")
@login_required
@student_required
def preview_id(id_id):
    school_id = SchoolID.query.get_or_404(id_id)
    student = Student.query.get_or_404(school_id.student_id)
    
    # Check if user owns this ID
    if student.user_id != current_user.id:
        flash('You do not have permission to view this', 'danger')
        return redirect(url_for('student.dashboard'))
    
    return render_template("student/review.html", school_id=school_id, student=student)


@student_bp.route("/id/<int:id_id>/download-pdf")
@login_required
@student_required
def download_id_pdf(id_id):
    school_id = SchoolID.query.get_or_404(id_id)
    student = Student.query.get_or_404(school_id.student_id)
    
    # Check if user owns this ID and it's approved
    if student.user_id != current_user.id:
        flash('You do not have permission to access this', 'danger')
        return redirect(url_for('student.dashboard'))
    
    if school_id.status not in ['approved', 'printed']:
        flash('Your ID is not approved yet', 'warning')
        return redirect(url_for('student.dashboard'))
    
    try:
        # Generate PDF if not already created
        if not school_id.pdf_file or not os.path.exists(os.path.join(current_app.root_path, school_id.pdf_file)):
            # Format student data for PDF generation
            valid_until_str = ''
            if student.valid_until:
                valid_until_str = student.valid_until.strftime('%b %Y')
            
            student_data = {
                'full_name': student.full_name,
                'reg_no': student.reg_no,
                'class_level': student.class_level or 'N/A',
                'course': student.course or 'N/A',
                'valid_until': valid_until_str,
                'photo_path': os.path.join(current_app.root_path, school_id.preview_image) if school_id.preview_image else None,
                'qr_path': os.path.join(current_app.root_path, school_id.qr_code) if school_id.qr_code else None,
                'blood_type': student.blood_type or 'N/A',
                'allergies': student.allergies or 'N/A',
                'emergency_contact_name': student.emergency_contact_name or 'N/A',
                'emergency_contact_phone': student.emergency_contact_phone or 'N/A',
                'school_name': student.school_name or 'School ID',
                'logo_path': os.path.join(current_app.root_path, 'static', 'img', 'logo.png')
            }
            
            pdf_filename = os.path.join(UPLOAD_FOLDER, 'pdfs', f"ID_{school_id.id_number}.pdf")
            os.makedirs(os.path.dirname(pdf_filename), exist_ok=True)
            
            try:
                # Call generate_id_pdf with proper format: list of students and output path
                pdf_path = generate_id_pdf([student_data], pdf_filename)
                print(f"PDF generation returned: {pdf_path}")
                print(f"PDF file exists: {os.path.exists(pdf_path) if pdf_path else 'N/A'}")
            except Exception as pdf_error:
                print(f"PDF generation error: {pdf_error}")
                import traceback
                traceback.print_exc()
                flash(f'Error generating PDF: {str(pdf_error)}', 'danger')
                return redirect(url_for('student.dashboard'))
            
            if pdf_path and os.path.exists(pdf_path):
                school_id.pdf_file = os.path.relpath(pdf_path, current_app.root_path)
                db.session.commit()
            else:
                flash('Failed to generate PDF', 'danger')
                return redirect(url_for('student.dashboard'))
        
        if not school_id.pdf_file:
            flash('PDF file path is invalid', 'danger')
            return redirect(url_for('student.dashboard'))
        
        pdf_path = os.path.join(current_app.root_path, school_id.pdf_file)
        
        if not os.path.exists(pdf_path):
            flash('PDF file not found', 'danger')
            return redirect(url_for('student.dashboard'))
        
        return send_file(pdf_path, as_attachment=True, download_name=f"ID_{school_id.id_number}.pdf")
        
    except Exception as e:
        flash(f'Error downloading PDF: {str(e)}', 'danger')
        return redirect(url_for('student.dashboard'))

