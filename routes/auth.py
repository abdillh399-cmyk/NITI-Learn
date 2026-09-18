from flask import Blueprint,render_template,redirect,url_for,flash,request
from flask_login import login_user,logout_user,login_required,current_user
from app import db
from models.user import User
auth_bp=Blueprint("auth",__name__)
@auth_bp.route("/register",methods=["GET","POST"])
def register():
    if current_user.is_authenticated:return redirect(url_for("main.index"))
    if request.method=="POST":
        username=request.form.get("username","").strip(); email=request.form.get("email","").strip().lower(); password=request.form.get("password",""); confirm=request.form.get("confirm_password","")
        if not username or not email or not password: flash("All fields are required.","danger")
        elif password!=confirm: flash("Passwords do not match.","danger")
        elif User.query.filter_by(email=email).first(): flash("Email already registered.","danger")
        elif User.query.filter_by(username=username).first(): flash("Username already taken.","danger")
        else:
            user=User(username=username,email=email); user.set_password(password); db.session.add(user); db.session.commit(); login_user(user); return redirect(url_for("main.index"))
    return render_template("auth/register.html")
@auth_bp.route("/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:return redirect(url_for("main.index"))
    if request.method=="POST":
        user=User.query.filter_by(email=request.form.get("email","").strip().lower()).first()
        if user and user.check_password(request.form.get("password","")): login_user(user,remember=bool(request.form.get("remember"))); return redirect(request.args.get("next") or url_for("main.index"))
        flash("Invalid email or password.","danger")
    return render_template("auth/login.html")
@auth_bp.route("/logout")
@login_required
def logout(): logout_user(); return redirect(url_for("main.index"))
@auth_bp.route("/profile")
@login_required
def profile(): return render_template("auth/profile.html",videos=current_user.videos)
