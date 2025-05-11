from flask import Blueprint, request, redirect, url_for, session, render_template, current_app
from services.supabase_service import get_supabase_client
from utils.time_utils import convert_to_vietnam_time
from datetime import datetime, timedelta
import json

history_bp = Blueprint('history', __name__)

@history_bp.route("/history", methods=["GET"])
def history():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    history_data = []
    total_records = 0
    total_pages = 1
    page = request.args.get('page', 1, type=int)
    error_message = None
    history_type = request.args.get('type', 'don_anh')
    user = {'taikhoan': '', 'Avarta': ''}

    try:
        # Lấy thông tin user
        try:
            supabase = get_supabase_client()
            user_response = supabase.table('taikhoan').select('taikhoan, Avarta').eq('id', session["user_id"]).execute()
            
            if not user_response.data or len(user_response.data) == 0:
                return redirect(url_for("auth.logout"))
            
            user = user_response.data[0]
        except Exception as e:
            current_app.logger.error(f"Lỗi khi lấy thông tin người dùng: {str(e)}")
            error_message = "Không thể lấy thông tin người dùng. Vui lòng thử lại sau."
            return render_template("history.html", 
                             username=user['taikhoan'], 
                             avatar_url=user['Avarta'],
                             history=history_data,
                             page=page,
                             total_pages=total_pages,
                             total_records=total_records,
                             history_type=history_type,
                             error_message=error_message)
        
        # Lấy tham số tìm kiếm và lọc
        search_query = request.args.get('search', '')
        confidence_filter = request.args.get('confidence', '')
        date_filter = request.args.get('date', '')
        sort_option = request.args.get('sort', 'newest')
        per_page = 8
        
        try:
            if history_type == 'don_anh':
                history_data, total_records, total_pages = get_single_image_history(
                    supabase, session["user_id"], search_query, 
                    confidence_filter, date_filter, sort_option, 
                    page, per_page)
            else:
                history_data, total_records, total_pages = get_group_history(
                    supabase, session["user_id"], search_query,
                    confidence_filter, date_filter, sort_option,
                    page, per_page)
                
        except Exception as api_error:
            current_app.logger.error(f"Lỗi API Supabase: {str(api_error)}")
            if "Worker threw exception" in str(api_error) or "Cloudflare" in str(api_error):
                error_message = "Máy chủ Supabase hiện đang gặp sự cố. Vui lòng thử lại sau."
            else:
                error_message = f"Lỗi khi truy vấn dữ liệu: {str(api_error)}"
            
        return render_template("history.html", 
                             username=user['taikhoan'], 
                             avatar_url=user['Avarta'],
                             history=history_data,
                             page=page,
                             total_pages=total_pages,
                             total_records=total_records,
                             history_type=history_type,
                             error_message=error_message)
                             
    except Exception as e:
        current_app.logger.error(f"Lỗi khi lấy lịch sử: {e}")
        return render_template("history.html", 
                             username="",
                             avatar_url="",
                             history=[],
                             page=1,
                             total_pages=1,
                             total_records=0,
                             error_message="Không thể tải lịch sử. Lỗi: " + str(e))

def get_single_image_history(supabase, user_id, search_query, confidence_filter, date_filter, sort_option, page, per_page):
    # Xây dựng query cơ bản
    count_query = supabase.table('lichsunhandien')\
        .select('id', count='exact')\
        .eq('user_id', int(user_id))\
        .eq('loai_nhan_dien', 'don_anh')
    
    history_query = supabase.table('lichsunhandien')\
        .select('id, hinh_anh, ket_qua, ten_san_pham, do_chinh_xac, thoi_gian, nhan_dien_thanh_cong, loai_nhan_dien, danh_gia')\
        .eq('user_id', int(user_id))\
        .eq('loai_nhan_dien', 'don_anh')
    
    # Áp dụng các bộ lọc
    apply_filters(count_query, history_query, search_query, confidence_filter, date_filter, sort_option)
    
    # Thực hiện truy vấn
    count_response = count_query.execute()
    total_records = count_response.count if hasattr(count_response, 'count') else 0
    total_pages = max(1, (total_records + per_page - 1) // per_page)
    offset = (page - 1) * per_page
    
    if page > total_pages:
        page = 1
        offset = 0
    
    history_response = history_query.range(offset, offset + per_page - 1).execute()
    history_data = history_response.data if history_response.data else []
    
    # Xử lý dữ liệu
    for item in history_data:
        process_history_item(item)
    
    return history_data, total_records, total_pages

def get_group_history(supabase, user_id, search_query, confidence_filter, date_filter, sort_option, page, per_page):
    # Tương tự như get_single_image_history nhưng cho nhóm
    count_query = supabase.table('nhom_ket_qua')\
        .select('id', count='exact')\
        .eq('user_id', int(user_id))
    
    history_query = supabase.table('nhom_ket_qua')\
        .select('*')\
        .eq('user_id', int(user_id))
    
    apply_filters(count_query, history_query, search_query, confidence_filter, date_filter, sort_option)
    
    count_response = count_query.execute()
    total_records = count_response.count if hasattr(count_response, 'count') else 0
    total_pages = max(1, (total_records + per_page - 1) // per_page)
    offset = (page - 1) * per_page
    
    if page > total_pages:
        page = 1
        offset = 0
    
    history_response = history_query.range(offset, offset + per_page - 1).execute()
    history_data = history_response.data if history_response.data else []
    
    for item in history_data:
        process_group_item(item)
    
    return history_data, total_records, total_pages

def apply_filters(count_query, history_query, search_query, confidence_filter, date_filter, sort_option):
    if search_query:
        count_query = count_query.ilike('ten_san_pham', f'%{search_query}%')
        history_query = history_query.ilike('ten_san_pham', f'%{search_query}%')
    
    if confidence_filter:
        apply_confidence_filter(count_query, history_query, confidence_filter)
    
    if date_filter:
        apply_date_filter(count_query, history_query, date_filter)
    
    if sort_option:
        apply_sort_option(history_query, sort_option)

def process_history_item(item):
    try:
        item['ket_qua'] = json.loads(item['ket_qua']) if isinstance(item['ket_qua'], str) else item['ket_qua']
        item['is_group'] = False
        
        if item['ket_qua'] and len(item['ket_qua']) > 0:
            confidence = item['ket_qua'][0]['confidence'] * 100
            if confidence >= 90:
                item['confidence_level'] = 'high'
            elif confidence >= 70:
                item['confidence_level'] = 'medium'
            else:
                item['confidence_level'] = 'low'
        
        if 'thoi_gian' in item and isinstance(item['thoi_gian'], str):
            vietnam_time = convert_to_vietnam_time(item['thoi_gian'])
            item['thoi_gian'] = vietnam_time.strftime('%Y-%m-%d %H:%M:%S')
    
    except (json.JSONDecodeError, Exception) as e:
        current_app.logger.error(f"Lỗi xử lý dữ liệu lịch sử: {str(e)}")
        item['ket_qua'] = []
        item['is_group'] = False

def process_group_item(item):
    try:
        confidence = item['do_chinh_xac'] * 100
        if confidence >= 90:
            item['confidence_level'] = 'high'
        elif confidence >= 70:
            item['confidence_level'] = 'medium'
        else:
            item['confidence_level'] = 'low'
        
        if 'thoi_gian' in item and isinstance(item['thoi_gian'], str):
            vietnam_time = convert_to_vietnam_time(item['thoi_gian'])
            item['thoi_gian'] = vietnam_time.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        current_app.logger.error(f"Lỗi xử lý dữ liệu nhóm: {str(e)}")

def apply_confidence_filter(count_query, history_query, confidence_filter):
    if confidence_filter == 'high':
        count_query = count_query.gte('do_chinh_xac', 0.9)
        history_query = history_query.gte('do_chinh_xac', 0.9)
    elif confidence_filter == 'medium':
        count_query = count_query.gte('do_chinh_xac', 0.7).lt('do_chinh_xac', 0.9)
        history_query = history_query.gte('do_chinh_xac', 0.7).lt('do_chinh_xac', 0.9)
    elif confidence_filter == 'low':
        count_query = count_query.lt('do_chinh_xac', 0.7)
        history_query = history_query.lt('do_chinh_xac', 0.7)

def apply_date_filter(count_query, history_query, date_filter):
    today = datetime.now()
    if date_filter == 'today':
        start_date = today.strftime('%Y-%m-%d')
        count_query = count_query.gte('thoi_gian', f'{start_date}T00:00:00')
        history_query = history_query.gte('thoi_gian', f'{start_date}T00:00:00')
    elif date_filter == 'week':
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        count_query = count_query.gte('thoi_gian', f'{start_date}T00:00:00')
        history_query = history_query.gte('thoi_gian', f'{start_date}T00:00:00')
    elif date_filter == 'month':
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        count_query = count_query.gte('thoi_gian', f'{start_date}T00:00:00')
        history_query = history_query.gte('thoi_gian', f'{start_date}T00:00:00')

def apply_sort_option(history_query, sort_option):
    if sort_option == 'newest':
        history_query = history_query.order('thoi_gian', desc=True)
    elif sort_option == 'oldest':
        history_query = history_query.order('thoi_gian', desc=False)
    elif sort_option == 'accuracy_high':
        history_query = history_query.order('do_chinh_xac', desc=True)
    elif sort_option == 'accuracy_low':
        history_query = history_query.order('do_chinh_xac', desc=False)
