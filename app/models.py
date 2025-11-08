from datetime import datetime
from flask_login import UserMixin
from . import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)  # "admin" o "user"
    pets = db.relationship("Pet", backref="owner", lazy=True)

    def is_admin(self) -> bool:
        return self.role == "admin"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Pet(db.Model):
    __tablename__ = "pets"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(120), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    appointments = db.relationship("Appointment", backref="pet", lazy=True, cascade="all, delete-orphan")
    treatments = db.relationship("Treatment", backref="pet", lazy=True, cascade="all, delete-orphan")


class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey("pets.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    appointment_type = db.Column(db.String(120), nullable=False)  # tipo_cita
    notes = db.Column(db.Text, nullable=True)


class Treatment(db.Model):
    __tablename__ = "treatments"
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey("pets.id"), nullable=False)
    treatment_type = db.Column(db.String(120), nullable=False)  # tipo
    applied_date = db.Column(db.Date, nullable=False)
    next_date = db.Column(db.Date, nullable=True)