from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models import db, Note, Prescription, Patient
from flask_login import login_required, current_user
from utils import encrypt_data, decrypt_data, role_required

records_bp = Blueprint('records', __name__)

#Admin: full CRUD
@records_bp.route('/notes', methods=['POST'])
@login_required
@role_required('admin', 'doctor')
def create_note():
    data = request.json
    note = Note(
        patient_id=data['patient_id'],
        content=encrypt_data(data['content']),
        is_sensitive=data.get('is_sensitive', False)
    )
    db.session.add(note)
    db.session.commit()
    return jsonify({"message": "Note created"}), 201

@records_bp.route('/notes', methods=['GET'])
@login_required
@role_required('admin', 'doctor', 'nurse')
def get_notes():
    notes = Note.query.all()
    visible = []
    for note in notes:
        if note.is_sensitive and current_user.role == 'nurse':
            continue
        visible.append({
            "id": note.id,
            "content": decrypt_data(note.content),
            "is_sensitive": note.is_senstive
        })
    return jsonify(visible)

@records_bp.route('/notes/<int:id>', methods=['PUT'])
@login_required
@role_required('admin', 'doctor')
def update_note(id):
    note = Note.query.get_or_404(id)
    data = request.json
    note.content = encrypt_data(data['content'])
    note.is_sensitive = data.get('is_sensitive', note.is_sensitive)
    db.session.commit()
    return jsonify({"message": "Note updated"})

@records_bp.route('/notes/<int:id>', methods=['DELETE'])
@login_required
@role_required('admin')
def delete_note(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted"})

#pharmacist: read-only prescriptions
@records_bp.route('/prescriptions', methods=['GET'])
@login_required
@role_required('admin', 'doctor', 'pharmacist')
def get_prescriptions():
    prescriptions = Prescription.query.all()
    return jsonify([
        {
            "id": p.id,
            "patient_id": p.patient_id,
            "drug_name": p.drug_name,
            "dosage" : p.dosage
        } for p in prescriptions
    ])

#create a prescription (admin, doctor)
@records_bp.route('/prescriptions', methods=['POST'])
@login_required
@role_required('admin', 'doctor')
def create_prescription():
    data = request.json
    prescription = Prescription(
        patient_id=data['patient_id'],
        drug_name=data['drug_name'],
        dosage=data['dosage']
    )
    db.session.add(prescription)
    db.session.commit()
    return jsonify({"message": "Prescription created"}), 201

#update a prescription (admin, doctor)
@records_bp.route('/prescriptions/<int:id>', methods=['PUT'])
@login_required
@role_required('admin', 'doctor')
def update_prescription(id):
    prescription = Prescription.query.get_or_404(id)
    data = request.json
    prescription.drug_name = data.get('drug_name', prescription.drug_name)
    prescription.dosage = data.get('dosage', prescription.dosage)
    db.session.commit()
    return jsonify({"message": "Prescription updated"})

#delte a prescription (admin only)
@records_bp.route('/prescriptions/<int:id>', methods=['DELETE'])
@login_required
@role_required('admin')
def delete_prescription(id):
    prescription = Prescription.query.get_or_404(id)
    db.session.delete(prescription)
    db.session.commit()
    return jsonify({"message": "Prescription deleted"})

@records_bp.route('/prescriptions', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'doctor')
def manage_prescriptions():
    if request.method == 'POST':
        data = request.form
        prescription = Prescription(
            patient_id = data['patient_id'],
            drug_name = data['drug_name'],
            dosage=data['dosage']
        )
        db.session(prescription)
        db.session.commit()
        return redirect(url_for('records.manage_prescriptions'))
    prescriptions = Prescription.query.all()
    return render_template("prescriptions.html", prescriptions=prescriptions, can_edit=current_user.role == 'admin')

@records_bp.route('/prescriptions/<int:id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_prescription_form(id):
    prescription = Prescription.query.get_or_404(id)
    db.session.delete(prescription)
    db.session.commit()
    return redirect(url_for('records.manage_prescriptions'))