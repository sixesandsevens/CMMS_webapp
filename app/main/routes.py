from app.main import bp
from flask import render_template

@bp.route('/')
def index():
    return "MaintainX Clone - Phase 2.5 Running"
