from flask import Blueprint, request, redirect, url_for, session, render_template, current_app, jsonify
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
        # Lấy thông tin user - tối ưu truy vấn
        try:
            supabase = get_supabase_client()
            user_response = supabase.table('taikhoan').select('taikhoan, Avarta').eq('id', session["user_id"]).limit(1).execute()
            
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
        per_page = 9
        
        try:
            # Giới hạn thời gian truy vấn và số lượng bản ghi
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
            if "Worker threw exception" in str(api_error) or "Cloudflare" in str(api_error) or "timed out" in str(api_error):
                error_message = "Máy chủ Supabase hiện đang gặp sự cố hoặc quá tải. Vui lòng thử lại sau."
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

@history_bp.route("/rate-result", methods=["POST"])
def rate_result():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Bạn cần đăng nhập để đánh giá."}), 401
    
    try:
        # Get rating data from request
        data = request.json
        result_id = data.get('result_id')
        rating = data.get('rating')
        
        # Validate input
        if not result_id or not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({
                "success": False, 
                "message": "Dữ liệu đánh giá không hợp lệ."
            }), 400
        
        # Update the rating in the database
        supabase = get_supabase_client()
        response = supabase.table('lichsunhandien').update({
            'danh_gia': rating
        }).eq('id', result_id).eq('user_id', session["user_id"]).execute()
        
        # Check if update was successful
        if response.data and len(response.data) > 0:
            current_app.logger.info(f"User {session['user_id']} rated result {result_id} with {rating} stars")
            return jsonify({
                "success": True, 
                "message": "Đánh giá của bạn đã được lưu. Cảm ơn!"
            })
        else:
            current_app.logger.warning(f"Rating failed: No record found for id {result_id} and user {session['user_id']}")
            return jsonify({
                "success": False, 
                "message": "Không tìm thấy kết quả nhận diện để đánh giá."
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Error rating result: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "Có lỗi xảy ra khi đánh giá. Vui lòng thử lại sau."
        }), 500

def get_single_image_history(supabase, user_id, search_query, confidence_filter, date_filter, sort_option, page, per_page):
    # Giảm số lượng bản ghi được tải về để tối ưu hóa
    max_records = 1000
    
    # Xây dựng query cơ bản
    count_query = supabase.table('lichsunhandien')\
        .select('id', count='estimated')\
        .eq('user_id', int(user_id))\
        .eq('loai_nhan_dien', 'don_anh')\
        .limit(max_records)
    
    history_query = supabase.table('lichsunhandien')\
        .select('id, hinh_anh, ket_qua, ten_san_pham, do_chinh_xac, thoi_gian, nhan_dien_thanh_cong, loai_nhan_dien, danh_gia')\
        .eq('user_id', int(user_id))\
        .eq('loai_nhan_dien', 'don_anh')
    
    # Áp dụng lọc theo thời gian trước tiên để giảm số lượng dữ liệu
    if date_filter:
        count_query, history_query = apply_date_filter(count_query, history_query, date_filter)
    
    # Áp dụng tìm kiếm
    if search_query:
        count_query = count_query.ilike('ten_san_pham', f'%{search_query}%')
        history_query = history_query.ilike('ten_san_pham', f'%{search_query}%')
    
    # Áp dụng lọc độ tin cậy
    if confidence_filter:
        count_query, history_query = apply_confidence_filter(count_query, history_query, confidence_filter)
    
    # Thực hiện truy vấn đếm
    try:
        count_response = count_query.execute()
        total_records = count_response.count if hasattr(count_response, 'count') else len(count_response.data)
    except Exception as e:
        current_app.logger.error(f"Error counting records: {str(e)}")
        total_records = 0
        
    total_pages = max(1, (total_records + per_page - 1) // per_page)
    page = min(page, total_pages)
    offset = (page - 1) * per_page
    
    # Sắp xếp và giới hạn kết quả
    apply_sort_option(history_query, sort_option)
    history_query = history_query.range(offset, offset + per_page - 1)
    
    try:
        history_response = history_query.execute()
        history_data = history_response.data if history_response.data else []
    except Exception as e:
        current_app.logger.error(f"Error fetching history: {str(e)}")
        history_data = []
    
    # Xử lý dữ liệu - sử dụng cấu trúc try-except cho từng bản ghi để tránh lỗi toàn bộ
    for item in history_data:
        try:
            process_history_item(item)
        except Exception as e:
            current_app.logger.error(f"Error processing history item: {str(e)}")
            # Thiết lập giá trị mặc định
            item['ket_qua'] = []
            item['is_group'] = False
            item['confidence_level'] = 'low'
    
    return history_data, total_records, total_pages

def get_group_history(supabase, user_id, search_query, confidence_filter, date_filter, sort_option, page, per_page):
    # Giảm số lượng bản ghi được tải về để tối ưu hóa
    max_records = 1000
    
    # Tương tự như get_single_image_history nhưng cho nhóm
    count_query = supabase.table('nhom_ket_qua')\
        .select('id', count='estimated')\
        .eq('user_id', int(user_id))\
        .limit(max_records)
    
    history_query = supabase.table('nhom_ket_qua')\
        .select('*')\
        .eq('user_id', int(user_id))
    
    # Áp dụng lọc theo thời gian trước tiên để giảm số lượng dữ liệu
    if date_filter:
        count_query, history_query = apply_date_filter(count_query, history_query, date_filter)
    
    if search_query:
        count_query = count_query.ilike('ten_nhom', f'%{search_query}%')
        history_query = history_query.ilike('ten_nhom', f'%{search_query}%')
    
    if confidence_filter:
        count_query, history_query = apply_confidence_filter(count_query, history_query, confidence_filter)
    
    # Thực hiện truy vấn đếm
    try:
        count_response = count_query.execute()
        total_records = count_response.count if hasattr(count_response, 'count') else len(count_response.data)
    except Exception as e:
        current_app.logger.error(f"Error counting group records: {str(e)}")
        total_records = 0
    
    total_pages = max(1, (total_records + per_page - 1) // per_page)
    page = min(page, total_pages)
    offset = (page - 1) * per_page
    
    # Sắp xếp và giới hạn kết quả
    apply_sort_option(history_query, sort_option)
    history_query = history_query.range(offset, offset + per_page - 1)
    
    try:
        history_response = history_query.execute()
        history_data = history_response.data if history_response.data else []
    except Exception as e:
        current_app.logger.error(f"Error fetching group history: {str(e)}")
        history_data = []
    
    # Xử lý dữ liệu một cách an toàn
    for item in history_data:
        try:
            process_group_item(item)
        except Exception as e:
            current_app.logger.error(f"Error processing group item: {str(e)}")
            # Thiết lập giá trị mặc định
            item['confidence_level'] = 'low'
    
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
        else:
            item['confidence_level'] = 'low'
        
        if 'thoi_gian' in item and isinstance(item['thoi_gian'], str):
            vietnam_time = convert_to_vietnam_time(item['thoi_gian'])
            item['thoi_gian'] = vietnam_time.strftime('%Y-%m-%d %H:%M:%S')
    
    except (json.JSONDecodeError, Exception) as e:
        current_app.logger.error(f"Lỗi xử lý dữ liệu lịch sử: {str(e)}")
        item['ket_qua'] = []
        item['is_group'] = False
        item['confidence_level'] = 'low'

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
        item['confidence_level'] = 'low'

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
    
    return count_query, history_query

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
    
    return count_query, history_query

def apply_sort_option(history_query, sort_option):
    if sort_option == 'newest':
        history_query = history_query.order('thoi_gian', desc=True)
    elif sort_option == 'oldest':
        history_query = history_query.order('thoi_gian', desc=False)
    elif sort_option == 'accuracy_high':
        history_query = history_query.order('do_chinh_xac', desc=True)
    elif sort_option == 'accuracy_low':
        history_query = history_query.order('do_chinh_xac', desc=False)
    
    return history_query
