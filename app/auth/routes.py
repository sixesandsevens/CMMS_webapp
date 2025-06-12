from app.auth import bp
from flask import render_template

@bp.route('/login')
def login():
    return "Login Page (To Be Implemented)"
