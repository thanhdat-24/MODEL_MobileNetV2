from flask import Blueprint, request, redirect, url_for, session, render_template, jsonify
from services.supabase_service import get_supabase_client
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/admin/cache-management", methods=["GET"])
def cache_management():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    supabase = get_supabase_client()
    user_response = supabase.table('taikhoan').select('taikhoan, Avarta').eq('id', session["user_id"]).execute()
    
    if not user_response.data or len(user_response.data) == 0:
        return redirect(url_for("auth.logout"))
    
    user = user_response.data[0]
    
    cache_response = supabase.table('cong_thuc_ai').select('*').order('su_dung_gan_nhat', desc=True).execute()
    cached_recipes = cache_response.data if cache_response.data else []
    
    return render_template("cache_management.html", 
                          username=user['taikhoan'], 
                          avatar_url=user['Avarta'],
                          cached_recipes=cached_recipes)

@admin_bp.route("/admin/clear-cache", methods=["POST"])
def clear_cache():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Bạn cần đăng nhập để thực hiện chức năng này"}), 401
    
    try:
        data = request.json
        action = data.get('action')
        
        supabase = get_supabase_client()
        
        if action == 'clear_all':
            supabase.table('cong_thuc_ai').delete().neq('id', 0).execute()
            return jsonify({"success": True, "message": "Đã xóa tất cả công thức đã cache"})
            
        elif action == 'clear_old':
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            supabase.table('cong_thuc_ai').delete().lt('su_dung_gan_nhat', thirty_days_ago).execute()
            return jsonify({"success": True, "message": "Đã xóa các công thức không sử dụng trong 30 ngày qua"})
            
        elif action == 'clear_item' and data.get('id'):
            supabase.table('cong_thuc_ai').delete().eq('id', data.get('id')).execute()
            return jsonify({"success": True, "message": "Đã xóa công thức được chọn"})
        
        return jsonify({"success": False, "message": "Hành động không hợp lệ"})
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500
