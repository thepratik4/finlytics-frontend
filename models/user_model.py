from datetime import datetime
from extensions import db

class User(db.Model):
    """
    Represents a registered user in the Finlytics system.
    Used for login/signup authentication.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email}>"

    def to_dict(self):
        """
        Returns a dictionary representation of the user, excluding sensitive info.
        """
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat()
        }
