
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import User, db
admin = Blueprint('admin', __name__)

@admin.route('/role_approval')
def role_approval():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    if user.role != 'admin':
        return redirect(url_for('auth.home'))
    users = User.query.filter_by(role='delivery_agent', approved=False).all()
    return render_template('role_approval.html', users=users)

@admin.route('/approve_user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    user = User.query.get(user_id)
    print(user)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('admin.role_approval'))
    user.approved = True
    db.session.commit()