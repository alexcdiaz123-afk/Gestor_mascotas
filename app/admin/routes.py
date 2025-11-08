from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from ..models import User, Pet, Appointment, Treatment

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin():
            abort(403)
        return func(*args, **kwargs)

    return wrapper


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    users = User.query.all()
    pets = Pet.query.all()
    appointments = Appointment.query.all()
    treatments = Treatment.query.all()
    stats = {
        "usuarios": len(users),
        "mascotas": len(pets),
        "citas": len(appointments),
        "tratamientos": len(treatments),
    }
    return render_template("admin/dashboard.html", users=users, pets=pets, appointments=appointments, treatments=treatments, stats=stats)