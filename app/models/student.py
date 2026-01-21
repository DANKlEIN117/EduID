from ..extensions import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(30), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    photo = db.Column(db.String(200))
