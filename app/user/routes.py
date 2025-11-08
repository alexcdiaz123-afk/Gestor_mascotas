from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from .. import db
from ..models import Pet, Appointment, Treatment

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/dashboard")
@login_required
def dashboard():
    pets = Pet.query.filter_by(owner_id=current_user.id).all()
    predictions = {}
    for pet in pets:
        try:
            predictions[pet.id] = current_app.predictor.estimate_next_date(pet)
        except Exception:
            predictions[pet.id] = None
    return render_template("user/dashboard.html", pets=pets, predictions=predictions)


@user_bp.route("/pets/new", methods=["GET", "POST"])
@login_required
def add_pet():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        species = request.form.get("species", "").strip()
        breed = request.form.get("breed", "").strip()
        age = int(request.form.get("age", 0))
        if not name or not species or age <= 0:
            flash("Nombre, especie y edad son obligatorios", "danger")
            return render_template("user/add_pet.html")
        pet = Pet(name=name, species=species, breed=breed, age=age, owner_id=current_user.id)
        db.session.add(pet)
        db.session.commit()
        flash("Mascota registrada", "success")
        return redirect(url_for("user.dashboard"))
    return render_template("user/add_pet.html")


@user_bp.route("/appointments/new", methods=["GET", "POST"])
@login_required
def schedule_appointment():
    pets = Pet.query.filter_by(owner_id=current_user.id).all()
    if request.method == "POST":
        pet_id = int(request.form.get("pet_id"))
        appointment_type = request.form.get("appointment_type", "Consulta")
        date_str = request.form.get("date", "")
        notes = request.form.get("notes", "")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Fecha inválida. Formato: YYYY-MM-DD", "danger")
            return render_template("user/schedule_appointment.html", pets=pets)

        pet = Pet.query.filter_by(id=pet_id, owner_id=current_user.id).first()
        if not pet:
            flash("Mascota no encontrada", "danger")
            return render_template("user/schedule_appointment.html", pets=pets)

        appt = Appointment(pet_id=pet.id, date=date, appointment_type=appointment_type, notes=notes)
        db.session.add(appt)
        db.session.commit()
        flash("Cita programada", "success")
        return redirect(url_for("user.dashboard"))
    return render_template("user/schedule_appointment.html", pets=pets)


@user_bp.route("/treatments/manage", methods=["GET", "POST"])
@login_required
def manage_treatments():
    pets = Pet.query.filter_by(owner_id=current_user.id).all()
    if request.method == "POST":
        pet_id = int(request.form.get("pet_id"))
        treatment_type = request.form.get("treatment_type", "Vacuna")
        applied_str = request.form.get("applied_date", "")
        next_str = request.form.get("next_date", "")
        try:
            applied_date = datetime.strptime(applied_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Fecha de aplicación inválida", "danger")
            return render_template("user/manage_treatments.html", pets=pets)
        next_date = None
        if next_str:
            try:
                next_date = datetime.strptime(next_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Próxima fecha inválida", "danger")
                return render_template("user/manage_treatments.html", pets=pets)

        pet = Pet.query.filter_by(id=pet_id, owner_id=current_user.id).first()
        if not pet:
            flash("Mascota no encontrada", "danger")
            return render_template("user/manage_treatments.html", pets=pets)

        tr = Treatment(pet_id=pet.id, treatment_type=treatment_type, applied_date=applied_date, next_date=next_date)
        db.session.add(tr)
        db.session.commit()
        flash("Tratamiento registrado", "success")
        return redirect(url_for("user.dashboard"))
    return render_template("user/manage_treatments.html", pets=pets)


@user_bp.route("/predictions")
@login_required
def predictions():
    pets = Pet.query.filter_by(owner_id=current_user.id).all()
    results = {}
    for pet in pets:
        try:
            appt = current_app.predictor.estimate_next_appointment_date(pet)
        except Exception:
            appt = None
        try:
            vac = current_app.predictor.estimate_next_vaccine_date(pet)
        except Exception:
            vac = None
        results[pet.id] = {"appointment": appt, "vaccine": vac}
    return render_template("user/predictions.html", pets=pets, results=results)


@user_bp.route("/agenda")
@login_required
def agenda():
    pets = Pet.query.filter_by(owner_id=current_user.id).all()
    pet_ids = [p.id for p in pets]
    appointments = Appointment.query.filter(Appointment.pet_id.in_(pet_ids)).order_by(Appointment.date.asc()).all()
    treatments = Treatment.query.filter(Treatment.pet_id.in_(pet_ids)).order_by(Treatment.applied_date.asc()).all()
    return render_template("user/agenda.html", pets=pets, appointments=appointments, treatments=treatments)