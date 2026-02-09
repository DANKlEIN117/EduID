from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.student import Student, SchoolID
from app.models import User
from app.forms import AdminReviewForm
from app.decorators import admin_required
from app.utils.pdf_utils import generate_bulk_print_pdf
from datetime import datetime
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
    # Get selected IDs from request
    selected_ids = request.json.get('ids', [])
    
    if not selected_ids:
        return jsonify({'success': False, 'message': 'No IDs selected'}), 400
    
    try:
        # Get SchoolID records
        school_ids = SchoolID.query.filter(SchoolID.id.in_(selected_ids)).all()
        
        if not school_ids:
            return jsonify({'success': False, 'message': 'No valid IDs found'}), 400
        
        # Prepare data for PDF generation
        id_records = []
        qr_paths = {}
        photo_paths = {}
        
        for sid in school_ids:
            student = Student.query.get(sid.student_id)
            id_records.append({
                'id': student.id,
                'full_name': student.full_name,
                'reg_no': student.reg_no,
                'class_level': student.class_level or 'N/A'
            })
            
            if sid.qr_code:
                qr_paths[student.id] = os.path.join(current_app.root_path, sid.qr_code)
            
            if sid.preview_image:
                photo_paths[student.id] = os.path.join(current_app.root_path, sid.preview_image)
        
        # Generate bulk PDF
        pdf_buffer = generate_bulk_print_pdf(id_records, qr_paths, photo_paths)
        
        if pdf_buffer:
            # Update status to printed for selected IDs
            for sid in school_ids:
                sid.status = 'printed'
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Print PDF generated successfully',
                'pdf_ready': True
            })
        else:
            return jsonify({'success': False, 'message': 'Error generating PDF'}), 500
            
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

