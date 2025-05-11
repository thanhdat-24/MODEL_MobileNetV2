from flask import Blueprint, request, redirect, url_for, session, render_template
from services.supabase_service import get_supabase_client

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        supabase = get_supabase_client()
        response = supabase.table('taikhoan').select('id, taikhoan, Avarta, matkhau').eq('taikhoan', username).eq('matkhau', password).execute()
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            session["user_id"] = user['id']
            return redirect(url_for("main.index"))
        else:
            return render_template("login.html", error="Tên người dùng hoặc mật khẩu không hợp lệ !")
    
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("auth.login"))