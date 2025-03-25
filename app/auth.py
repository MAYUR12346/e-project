from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
import re
from .models import User,db


from flask_mail import Message
from app import mail


auth_bp = Blueprint('auth', __name__)


def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    pattern = r'^\d{10}$'
    return re.match(pattern, phone) is not None

def send_reset_email(user, token):
    """Send a password reset email to the user"""
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    msg = Message(
        'Password Reset Request',
        recipients=[user.email]
    )
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email and no changes will be made.

This link will expire in 1 hour.
'''
    mail.send(msg)

@auth_bp.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for("auth.login"))
    user = User.query.get(session['user_id'])
    return render_template("home.html")

@auth_bp.route("/account")
def account():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    return render_template("account.html", user=user)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if 'user_id' in session:
        return redirect(url_for("auth.home"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        print(email, password)

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_id'] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("auth.home"))
        else:
            flash("Invalid email or password!", "danger")

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        address = request.form["address"]
        state = request.form["state"]
        city = request.form["city"]
        pincode = request.form["pincode"]
        role = request.form["role"]

        print(name, phone, email, password, confirm_password, address, state, city, pincode)
        # Validation
        if not all([name, phone, email, password, confirm_password, address, state, city, pincode]):
            flash("All fields are required!", "danger")
            return render_template("registration.html")

        if not is_valid_email(email):
            flash("Invalid email format!", "danger")
            return render_template("registration.html")

        if not is_valid_phone(phone):
            flash("Invalid phone number! Please enter 10 digits.", "danger")
            return render_template("registration.html")

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return render_template("registration.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return render_template("registration.html")

        new_user = User(
            name=name,
            phone=phone,
            email=email,
            password=password,
            address=address,
            state=state,
            city=city,
            pincode=pincode,
            role=role
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "danger")

    return render_template("registration.html")
    # return ("Hello, registration")

@auth_bp.route("/update-password", methods=["GET", "POST"])
def update_password():
    if 'user_id' not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        user = User.query.get(session['user_id'])
        
        if not user.password == current_password:
            flash("Current password is incorrect!", "danger")
        elif new_password != confirm_password:
            flash("New passwords do not match!", "danger")
        else:
            user.password = new_password
            db.session.commit()
            flash("Password updated successfully!", "success")
            return redirect(url_for("auth.home"))

    return render_template("update_password.html")


@auth_bp.route("/update-profile", methods=["GET", "POST"])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session['user_id'])
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        state = request.form.get("state", "").strip()
        city = request.form.get("city", "").strip()
        pincode = request.form.get("pincode", "").strip()

        # Validate required fields
        if not all([name, phone, address, state, city, pincode]):
            flash("All fields are required!", "warning")
            return redirect(url_for("auth.update_profile"))

        user.name = name
        user.phone = phone
        user.address = address
        user.state = state
        user.city = city
        user.pincode = pincode

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating profile.", "danger")

        return redirect(url_for("auth.home"))

    return render_template("update_profile.html", current_user=user)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate a reset token
            token = user.generate_reset_token(current_app.config['SECRET_KEY'])
            
            # Send a reset email
            send_reset_email(user, token)
            
            flash("Password reset email sent. Please check your email.", "info")
            
            return render_template("email_sent.html", email=email)
    
    return render_template("forgot_password.html")

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # Verify the token
    user = User.verify_reset_token(token, current_app.config['SECRET_KEY'])
    
    if not user:
        flash("Invalid or expired reset token. Please try again.", "danger")
        return redirect(url_for("auth.forgot_password"))
    
    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]
        
        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
        else:
            # Update the user's password
            user.password = new_password
            user.reset_token = None
            user.reset_token_expiry = None
            db.session.commit()
            
            flash("Your password has been updated successfully!", "success")
            return redirect(url_for("auth.login"))
    
    return render_template("reset_password.html")

@auth_bp.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully!", "success")
    return redirect(url_for("auth.login"))

@auth_bp.context_processor
def inject_user():
    from .models import User
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return {'current_user': user}
    return {'current_user': None}
