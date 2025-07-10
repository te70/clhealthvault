from flask import Blueprint
from .records import records_bp

def register_blueprints(app):
    app.register_blueprint(records_bp)