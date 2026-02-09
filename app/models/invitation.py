from ..extensions import db
from datetime import datetime, timedelta
import secrets

class AdminInvitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(256), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # who created the invite
    used_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # who accepted it
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))
    used_at = db.Column(db.DateTime)
    is_used = db.Column(db.Boolean, default=False)

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)

    def is_valid(self):
        """Check if invitation is still valid"""
        if self.is_used:
            return False
        if datetime.utcnow() > self.expires_at:
            return False
        return True

    def mark_as_used(self, user_id):
        """Mark invitation as used"""
        self.is_used = True
        self.used_at = datetime.utcnow()
        self.used_by_id = user_id
