from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import db, Patient, Note, Prescription
from utils import role_required
from utils import encrypt_data, decrypt_data

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'doctor')
def dashboard():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'patient':
            db.session.add(Patient(name=request.form['name']))
        elif form_type == 'note':
            encrypted = encrypt_data(request.form['content'])
            note = Note(
                patient_id=request.form['patient_id'],
                content=encrypted,
                is_sensitive='is_sensitive' in request.form
            )
            db.session.add(note)
        elif form_type == 'prescription':
            db.session.add(Prescription(
                patient_id=request.form['patient_id'],
                drug_name=request.form['drug_name'],
                dosage=request.form['dosage']
            ))
        db.session.commit()
        return redirect(url_for('dashboard.dashboard'))

    patients = Patient.query.all()
    notes = [
        {
            "id": n.id,
            "patient_id": n.patient_id,
            "content": decrypt_data(n.content),
            "is_sensitive": n.is_sensitive
        } for n in Note.query.all()
    ]
    prescriptions = Prescription.query.all()

    

    return render_template('dashboard.html', patients=patients, notes=notes, prescriptions=prescriptions)
