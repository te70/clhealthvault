from flask import Blueprint
from .records import records_bp
from .dashboard import dashboard_bp

def register_blueprints(app):
    app.register_blueprint(records_bp)
    app.register_blueprint(dashboard_bp)