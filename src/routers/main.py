from flask import Blueprint, redirect, url_for, session, render_template
from services.supabase_service import get_supabase_client

main_bp = Blueprint('main', __name__)

@main_bp.route("/", methods=["GET"])
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    supabase = get_supabase_client()
    response = supabase.table('taikhoan').select('taikhoan, Avarta').eq('id', session["user_id"]).execute()
    
    if not response.data or len(response.data) == 0:
        return redirect(url_for("auth.logout"))
    
    user = response.data[0]
    return render_template("index.html", username=user['taikhoan'], avatar_url=user['Avarta'])

@main_bp.route("/shop", methods=["GET"])
def shop():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    supabase = get_supabase_client()
    response = supabase.table('taikhoan').select('taikhoan, Avarta').eq('id', session["user_id"]).execute()
    
    if not response.data or len(response.data) == 0:
        return redirect(url_for("auth.logout"))
    
    user = response.data[0]
    return render_template("shop.html", username=user['taikhoan'], avatar_url=user['Avarta'])

@main_bp.route("/news", methods=["GET"])
def news():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    supabase = get_supabase_client()
    response = supabase.table('taikhoan').select('taikhoan, Avarta').eq('id', session["user_id"]).execute()
    
    if not response.data or len(response.data) == 0:
        return redirect(url_for("auth.logout"))
    
    user = response.data[0]
    return render_template("news.html", username=user['taikhoan'], avatar_url=user['Avarta'])