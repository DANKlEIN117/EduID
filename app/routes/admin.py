from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.student import Student, SchoolID
from app.models import User
from app.models.invitation import AdminInvitation
from app.forms import AdminReviewForm, AdminInviteForm
from app.decorators import admin_required
from app.utils.pdf_utils import generate_bulk_print_pdf
from datetime import datetime, timedelta
import os

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    # Statistics
    total_submissions = SchoolID.query.count()
    pending_submissions = SchoolID.query.filter_by(status='pending').count()
    approved_ids = SchoolID.query.filter_by(status='approved').count()
    printed_ids = SchoolID.query.filter_by(status='printed').count()
    rejected_ids = SchoolID.query.filter_by(status='rejected').count()
    
    # Recent submissions
    recent = SchoolID.query.order_by(SchoolID.submission_date.desc()).limit(5).all()
    
    stats = {
        'total': total_submissions,
        'pending': pending_submissions,
        'approved': approved_ids,
        'printed': printed_ids,
        'rejected': rejected_ids
    }
    
    return render_template("admin/dashboard.html", stats=stats, recent=recent)


@admin_bp.route("/submissions")
@login_required
@admin_required
def submissions():
    # Filter by status
    status_filter = request.args.get('status', 'pending')
    page = request.args.get('page', 1, type=int)
    
    if status_filter and status_filter != 'all':
        query = SchoolID.query.filter_by(status=status_filter)
    else:
        query = SchoolID.query
    
    submissions = query.order_by(SchoolID.submission_date.desc()).paginate(page=page, per_page=10)
    
    return render_template("admin/submissions.html", submissions=submissions, current_status=status_filter)


@admin_bp.route("/submission/<int:id_id>/review", methods=['GET', 'POST'])
@login_required
@admin_required
def review_submission(id_id):
    school_id = SchoolID.query.get_or_404(id_id)
    student = Student.query.get_or_404(school_id.student_id)
    
    form = AdminReviewForm()
    
    if form.validate_on_submit():
        school_id.status = form.status.data
        school_id.approval_date = datetime.utcnow()
        
        if form.status.data == 'rejected':
            school_id.rejection_reason = form.rejection_reason.data
        
        school_id.notes = form.notes.data
        
        db.session.commit()
        
        action = 'approved' if form.status.data == 'approved' else 'rejected'
        flash(f'ID {action} successfully', 'success')
        return redirect(url_for('admin.submissions', status='pending'))
    
    return render_template("admin/review_submission.html", school_id=school_id, student=student, form=form)


@admin_bp.route("/submission/<int:id_id>/approve", methods=['POST'])
@login_required
@admin_required
def approve_submission(id_id):
    school_id = SchoolID.query.get_or_404(id_id)
    
    school_id.status = 'approved'
    school_id.approval_date = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'ID approved successfully'})


@admin_bp.route("/submission/<int:id_id>/reject", methods=['POST'])
@login_required
@admin_required
def reject_submission(id_id):
    school_id = SchoolID.query.get_or_404(id_id)
    reason = request.json.get('reason', '')
    
    school_id.status = 'rejected'
    school_id.rejection_reason = reason
    school_id.approval_date = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'ID rejected successfully'})


@admin_bp.route("/submission/<int:id_id>/mark-printed", methods=['POST'])
@login_required
@admin_required
def mark_printed(id_id):
    school_id = SchoolID.query.get_or_404(id_id)
    
    school_id.status = 'printed'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'ID marked as printed'})


@admin_bp.route("/bulk-print")
@login_required
@admin_required
def bulk_print():
    # Get all approved but not yet printed IDs
    approved_ids = SchoolID.query.filter_by(status='approved').all()
    
    return render_template("admin/bulk_print.html", school_ids=approved_ids)


@admin_bp.route("/generate-print-pdf", methods=['POST'])
@login_required
@admin_required
def generate_print_pdf():
    print(f"Request method: {request.method}")
    print(f"Request content-type: {request.content_type}")
    
    # Get selected IDs from request
    selected_ids = []
    
    try:
        if not request.is_json:
            print("Request is not JSON")
            return jsonify({'success': False, 'message': 'Request must be JSON'}), 400
            
        data = request.get_json()
        print(f"Request data: {data}")
        
        selected_ids = data.get('ids', [])
        print(f"Selected IDs from request: {selected_ids}")
        
        # Convert string IDs to integers
        selected_ids = [int(id_val) for id_val in selected_ids]
        print(f"Converted IDs: {selected_ids}")
        
    except Exception as json_error:
        print(f"Error parsing JSON: {json_error}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error parsing request: {str(json_error)}'}), 400
    
    if not selected_ids or len(selected_ids) == 0:
        print("No IDs selected")
        return jsonify({'success': False, 'message': 'No IDs selected'}), 400
    
    try:
        # Get SchoolID records
        school_ids = SchoolID.query.filter(SchoolID.id.in_(selected_ids)).all()
        print(f"Found {len(school_ids)} school IDs")
        
        if not school_ids:
            return jsonify({'success': False, 'message': 'No valid IDs found'}), 400
        
        # Prepare data for PDF generation
        id_records = []
        qr_paths = {}
        photo_paths = {}
        
        for sid in school_ids:
            student = Student.query.get(sid.student_id)
            if not student:
                continue
                
            id_records.append({
                'id': student.id,
                'full_name': student.full_name,
                'reg_no': student.reg_no,
                'class_level': student.class_level or 'N/A',
                'course': getattr(student, 'course', None) or getattr(student, 'program', None) or student.class_level,
                'year': getattr(student, 'year_of_study', None) or getattr(student, 'year', None) or '',
                'valid_until': (datetime.utcnow() + timedelta(days=365)).strftime('%b %Y'),
                'blood_type': student.blood_type,
                'allergies': student.allergies,
                'emergency_contact_name': student.emergency_contact_name,
                'emergency_contact_phone': student.emergency_contact_phone,
                'school_name': student.school_name or 'School ID'
            })
            
            if sid.qr_code:
                qr_paths[student.id] = os.path.join(current_app.root_path, sid.qr_code)
            
            if sid.preview_image:
                photo_paths[student.id] = os.path.join(current_app.root_path, sid.preview_image)
        
        if not id_records:
            return jsonify({'success': False, 'message': 'No valid students found'}), 400
        
        # School configuration (use first student's school if available)
        default_logo = os.path.join(current_app.root_path, 'static', 'img', 'logo.png')
        school_config = {
            'name': id_records[0].get('school_name', 'School ID'),
            'motto': 'Excellence in Education',
            'color': '#1a5490',
            'logo_path': default_logo if os.path.exists(default_logo) else None,
            'address': current_app.config.get('SCHOOL_ADDRESS'),
            'website': current_app.config.get('SCHOOL_WEBSITE')
        }
        
        print(f"Generating bulk PDF for {len(id_records)} students")
        
        # Generate bulk PDF
        try:
            pdf_buffer = generate_bulk_print_pdf(id_records, qr_paths, photo_paths, school_config)
        except Exception as pdf_error:
            print(f"Bulk PDF generation error: {pdf_error}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'PDF generation error: {str(pdf_error)}'}), 500

        if not pdf_buffer:
            return jsonify({'success': False, 'message': 'PDF buffer is empty'}), 500

        # Mark selected IDs as printed
        try:
            for sid in school_ids:
                sid.status = 'printed'
            db.session.commit()
        except Exception as commit_error:
            print(f"Error updating printed status: {commit_error}")

        # Return PDF as attachment for download
        try:
            pdf_buffer.seek(0)
            filename = f"bulk_print_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
            return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)
        except Exception as send_error:
            print(f"Error sending PDF: {send_error}")
            return jsonify({'success': False, 'message': f'Error sending PDF: {str(send_error)}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route("/students")
@login_required
@admin_required
def students_list():
    page = request.args.get('page', 1, type=int)
    students = Student.query.paginate(page=page, per_page=10)
    
    return render_template("admin/students.html", students=students)


@admin_bp.route("/student/<int:student_id>")
@login_required
@admin_required
def student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    school_ids = SchoolID.query.filter_by(student_id=student_id).order_by(SchoolID.submission_date.desc()).all()
    
    return render_template("admin/student_detail.html", student=student, school_ids=school_ids)


@admin_bp.route("/statistics")
@login_required
@admin_required
def statistics():
    # Get statistics by month
    total_submissions = SchoolID.query.count()
    pending = SchoolID.query.filter_by(status='pending').count()
    approved = SchoolID.query.filter_by(status='approved').count()
    rejected = SchoolID.query.filter_by(status='rejected').count()
    printed = SchoolID.query.filter_by(status='printed').count()
    
    stats = {
        'total': total_submissions,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'printed': printed,
        'approval_rate': round((approved / total_submissions * 100) if total_submissions > 0 else 0, 2)
    }
    
    return render_template("admin/statistics.html", stats=stats)


@admin_bp.route("/invite-admin", methods=['GET', 'POST'])
@login_required
@admin_required
def invite_admin():
    form = AdminInviteForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        
        # Check if already invited
        existing = AdminInvitation.query.filter_by(email=email, is_used=False).first()
        if existing and existing.is_valid():
            flash('An invitation has already been sent to this email', 'warning')
            return render_template('admin/invite_admin.html', form=form)
        
        token = AdminInvitation.generate_token()
        invitation = AdminInvitation(
            token=token,
            email=email,
            admin_id=current_user.id
        )
        db.session.add(invitation)
        db.session.commit()
        
        # Create invitation link
        invite_link = url_for('auth.register_admin', token=token, _external=True)
        
        flash(f'Invitation sent! Share this link: {invite_link}', 'success')
        return render_template('admin/invite_admin.html', form=form, invite_link=invite_link)
    
    # Show pending invitations
    pending = AdminInvitation.query.filter_by(is_used=False).filter(AdminInvitation.expires_at > datetime.utcnow()).all()
    
    return render_template('admin/invite_admin.html', form=form, pending_invitations=pending)


@admin_bp.route("/invitations")
@login_required
@admin_required
def invitations():
    page = request.args.get('page', 1, type=int)
    
    # All invitations
    invitations = AdminInvitation.query.order_by(AdminInvitation.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('admin/invitations.html', invitations=invitations)


