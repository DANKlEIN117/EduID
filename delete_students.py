#!/usr/bin/env python
"""
Delete all Student records and optionally remove photos from uploads/photos.
Creates CSV backup of students at uploads/backups/students_backup_<timestamp>.csv
"""
import os
import csv
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models.student import Student

BACKUP_DIR = os.path.join('uploads', 'backups')
PHOTOS_DIR = os.path.join('uploads', 'photos')


def full_path(app_root, path_value):
    if not path_value:
        return None
    if os.path.isabs(path_value):
        return path_value
    return os.path.join(app_root, path_value.lstrip('/\\'))


def backup_and_delete_students(delete_photos=True):
    app = create_app()
    with app.app_context():
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        backup_path = os.path.join(BACKUP_DIR, f'students_backup_{timestamp}.csv')

        students = Student.query.all()
        print(f'Found {len(students)} student record(s) to back up and delete')

        # Write CSV backup
        with open(backup_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['id','user_id','reg_no','full_name','school_name','course','email','phone','date_of_birth','class_level','valid_until','photo','blood_type','allergies','emergency_contact_name','emergency_contact_phone','created_at','updated_at'])
            for s in students:
                writer.writerow([
                    s.id, s.user_id, s.reg_no, s.full_name, s.school_name or '', s.course or '', s.email or '', s.phone or '',
                    s.date_of_birth.isoformat() if s.date_of_birth else '', s.class_level or '', s.valid_until.isoformat() if s.valid_until else '',
                    s.photo or '', s.blood_type or '', s.allergies or '', s.emergency_contact_name or '', s.emergency_contact_phone or '',
                    s.created_at.isoformat() if s.created_at else '', s.updated_at.isoformat() if s.updated_at else ''
                ])

        print(f'Students CSV backup written to: {backup_path}')

        deleted_files = 0
        if delete_photos:
            for s in students:
                fp = full_path(app.root_path, s.photo) if s.photo else None
                if fp and os.path.exists(fp):
                    try:
                        os.remove(fp)
                        deleted_files += 1
                        print(f'Deleted photo: {fp}')
                    except Exception as e:
                        print(f'Failed to delete photo {fp}: {e}')

            # Optionally remove any remaining files in uploads/photos dir
            photos_dir = os.path.join(app.root_path, PHOTOS_DIR)
            if os.path.exists(photos_dir) and os.path.isdir(photos_dir):
                for root, dirs, files in os.walk(photos_dir):
                    for f in files:
                        try:
                            os.remove(os.path.join(root, f))
                            deleted_files += 1
                        except Exception:
                            pass

        # Delete student records
        count = len(students)
        if count > 0:
            try:
                db.session.query(Student).delete(synchronize_session=False)
                db.session.commit()
                print(f'Deleted {count} Student record(s) from database')
            except Exception as e:
                db.session.rollback()
                print(f'Error deleting Student records: {e}')
        else:
            print('No Student records to delete')

        print(f'Photos deleted: {deleted_files}')
        print('Operation complete.')

if __name__ == '__main__':
    backup_and_delete_students(delete_photos=True)
