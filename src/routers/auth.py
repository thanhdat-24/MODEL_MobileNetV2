from flask import Blueprint, request, redirect, url_for, session, render_template, flash, current_app
from services.supabase_service import get_supabase_client
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # If user is already logged in, redirect appropriately
    if "user_id" in session:
        if session.get("is_admin"):
            current_app.logger.info(f"Already logged in as admin, redirecting to dashboard")
            return redirect(url_for("admin.dashboard"))
        else:
            current_app.logger.info(f"Already logged in as user, redirecting to index")
            return redirect(url_for("main.index"))

    if request.method == "POST":
        taikhoan = request.form.get("taikhoan")
        matkhau = request.form.get("matkhau")

        current_app.logger.info(f"Login attempt for user: {taikhoan}")

        if not taikhoan or not matkhau:
            flash("Vui lòng nhập đầy đủ thông tin đăng nhập", "error")
            return render_template("login.html")

        try:
            supabase = get_supabase_client()
            current_app.logger.info("Supabase client connected successfully")
            
            response = supabase.table('taikhoan').select('id, taikhoan, matkhau, is_admin').eq('taikhoan', taikhoan).execute()
            current_app.logger.info(f"Query response: {response.data}")
            
            if response.data and len(response.data) > 0:
                user = response.data[0]
                current_app.logger.info(f"Found user: {user}")
                
                # Verify password - implement proper password hashing in real application
                if matkhau == user['matkhau']:  # In a real app, use bcrypt.checkpw()
                    # Make the session permanent
                    session.permanent = True
                    
                    session["user_id"] = user["id"]
                    session["username"] = user["taikhoan"]
                    
                    # Check if is_admin exists in the user data
                    if 'is_admin' in user:
                        session["is_admin"] = user["is_admin"]
                        current_app.logger.info(f"Admin status: {session['is_admin']}")
                    else:
                        session["is_admin"] = False
                        current_app.logger.info("is_admin field not found, defaulting to False")
                    
                    # Redirect to admin dashboard if user is admin
                    if session.get("is_admin"):
                        current_app.logger.info(f"Redirecting admin user {taikhoan} to dashboard")
                        return redirect(url_for("admin.dashboard"))
                    else:
                        current_app.logger.info(f"Redirecting regular user {taikhoan} to index")
                        return redirect(url_for("main.index"))
                else:
                    current_app.logger.info("Password incorrect")
                    flash("Mật khẩu không chính xác", "error")
            else:
                current_app.logger.info("User not found")
                flash("Tài khoản không tồn tại", "error")
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            flash(f"Lỗi đăng nhập: {str(e)}", "error")

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    current_app.logger.info(f"Logging out user: {session.get('username')}")
    session.clear()
    return redirect(url_for("auth.login"))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        taikhoan = request.form.get("taikhoan")
        matkhau = request.form.get("matkhau")
        confirm_matkhau = request.form.get("confirm_matkhau")

        if not taikhoan or not matkhau or not confirm_matkhau:
            flash("Vui lòng nhập đầy đủ thông tin đăng ký", "error")
            return render_template("register.html")

        if matkhau != confirm_matkhau:
            flash("Mật khẩu xác nhận không khớp", "error")
            return render_template("register.html")

        try:
            supabase = get_supabase_client()
            
            # Check if username already exists
            response = supabase.table('taikhoan').select('id').eq('taikhoan', taikhoan).execute()
            
            if response.data and len(response.data) > 0:
                flash("Tài khoản đã tồn tại", "error")
                return render_template("register.html")
            
            # In a real app, hash the password before storing it
            # hashed_password = bcrypt.hashpw(matkhau.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create new user
            response = supabase.table('taikhoan').insert({
                "taikhoan": taikhoan,
                "matkhau": matkhau,  # Use hashed_password in real app
                "Avarta": "https://www.gravatar.com/avatar/?d=mp",
                "is_admin": False  # Default to non-admin
            }).execute()
            
            if response.data and len(response.data) > 0:
                flash("Đăng ký thành công! Bây giờ bạn có thể đăng nhập.", "success")
                return redirect(url_for("auth.login"))
            else:
                flash("Đăng ký thất bại. Vui lòng thử lại.", "error")
        except Exception as e:
            flash(f"Lỗi đăng ký: {str(e)}", "error")

    return render_template("register.html")