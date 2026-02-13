#!/usr/bin/env python
"""
Backup and delete all SchoolID records and associated uploaded files.
Creates CSV backup at `uploads/backups/schoolids_backup_<timestamp>.csv`.
Deletes files referenced by SchoolID (qr_code, preview_image, pdf_file) and clears uploads/pdfs, uploads/photos, uploads/qr_codes.
"""
import os
import csv
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models.student import SchoolID, Student

BACKUP_DIR = os.path.join('uploads', 'backups')
UPLOAD_DIRS = [os.path.join('uploads', 'pdfs'), os.path.join('uploads', 'photos'), os.path.join('uploads', 'qr_codes')]


def full_path(app_root, path_value):
    if not path_value:
        return None
    # If absolute path, return as-is
    if os.path.isabs(path_value):
        return path_value
    # Strip leading slash if present
    cleaned = path_value.lstrip('/\\')
    return os.path.join(app_root, cleaned)


def backup_and_delete():
    app = create_app()
    with app.app_context():
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        backup_path = os.path.join(BACKUP_DIR, f'schoolids_backup_{timestamp}.csv')

        schoolids = SchoolID.query.all()
        print(f'Found {len(schoolids)} SchoolID record(s) to back up and delete')

        # Write CSV backup
        with open(backup_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['id', 'id_number', 'student_id', 'student_reg_no', 'student_name', 'status', 'submission_date', 'approval_date', 'qr_code', 'preview_image', 'pdf_file', 'notes', 'created_at', 'updated_at'])
            for s in schoolids:
                student_reg = None
                student_name = None
                try:
                    if s.student:
                        student_reg = s.student.reg_no
                        student_name = s.student.full_name
                except Exception:
                    pass
                writer.writerow([
                    s.id, s.id_number, s.student_id, student_reg, student_name, s.status,
                    s.submission_date.isoformat() if s.submission_date else '',
                    s.approval_date.isoformat() if s.approval_date else '',
                    s.qr_code or '', s.preview_image or '', s.pdf_file or '',
                    s.notes or '', s.created_at.isoformat() if s.created_at else '', s.updated_at.isoformat() if s.updated_at else ''
                ])

        print(f'CSV backup written to: {backup_path}')

        # Delete files referenced by SchoolID records
        deleted_files = 0
        for s in schoolids:
            for field in ('qr_code', 'preview_image', 'pdf_file'):
                val = getattr(s, field)
                fp = full_path(app.root_path, val)
                if fp and os.path.exists(fp):
                    try:
                        os.remove(fp)
                        deleted_files += 1
                        print(f'Deleted file: {fp}')
                    except Exception as e:
                        print(f'Failed to delete file {fp}: {e}')

        # Also remove leftover files inside standard upload dirs
        removed_extra = 0
        for up in UPLOAD_DIRS:
            dirpath = os.path.join(app.root_path, up)
            if os.path.exists(dirpath) and os.path.isdir(dirpath):
                for root, dirs, files in os.walk(dirpath):
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            os.remove(fp)
                            removed_extra += 1
                        except Exception as e:
                            print(f'Failed to delete file {fp}: {e}')

        # Delete all SchoolID records
        count = len(schoolids)
        if count > 0:
            try:
                # Use bulk delete for speed
                db.session.query(SchoolID).delete(synchronize_session=False)
                db.session.commit()
                print(f'Deleted {count} SchoolID record(s) from database')
            except Exception as e:
                db.session.rollback()
                print(f'Error deleting SchoolID records: {e}')
        else:
            print('No SchoolID records to delete')

        print(f'Files deleted referenced by records: {deleted_files}; additional files removed from upload dirs: {removed_extra}')
        print('Operation complete.')

if __name__ == "__main__":
    backup_and_delete()
