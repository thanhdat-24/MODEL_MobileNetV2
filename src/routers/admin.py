from flask import Blueprint, request, redirect, url_for, session, render_template, jsonify, flash, current_app
from services.supabase_service import get_supabase_client
from datetime import datetime, timedelta
import os
import json
from functools import wraps
import tensorflow as tf
from config import IMG_SIZE, CONFIDENCE_THRESHOLD, MODEL_SAVE_PATH

admin_bp = Blueprint('admin', __name__)

# Decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bạn cần đăng nhập để truy cập trang này.', 'error')
            return redirect(url_for('auth.login'))
        
        if 'is_admin' not in session or not session['is_admin']:
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('main.index'))
            
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/admin/dashboard", methods=["GET"])
@admin_required
def dashboard():
    supabase = get_supabase_client()
    
    # Get statistics
    try:
        # Get logged in user info
        user_id = session.get('user_id')
        username = session.get('username')
        
        # Giới hạn số lượng dữ liệu để tránh timeout
        records_limit = 8  # Tăng từ 5 lên 8 bản ghi hiển thị trên dashboard
        
        # Total users - sử dụng limit để tránh phải đếm toàn bộ
        user_response = supabase.table('taikhoan').select('id', count='estimated').limit(1000).execute()
        total_users = user_response.count if hasattr(user_response, 'count') else len(user_response.data)
        
        # Total recognitions - sử dụng limit để tránh phải đếm toàn bộ
        recognition_response = supabase.table('lichsunhandien').select('id', count='estimated').limit(1000).execute()
        total_recognitions = recognition_response.count if hasattr(recognition_response, 'count') else len(recognition_response.data)
        
        # Success rate - chỉ đếm số lượng giới hạn để tính tỉ lệ
        success_response = supabase.table('lichsunhandien').select('id', count='estimated').eq('nhan_dien_thanh_cong', True).limit(1000).execute()
        success_count = success_response.count if hasattr(success_response, 'count') else len(success_response.data)
        success_rate = round((success_count / total_recognitions * 100) if total_recognitions > 0 else 0, 1)
        
        # Average rating - chỉ lấy mẫu đánh giá gần đây nhất
        rating_response = supabase.table('lichsunhandien').select('danh_gia').gt('danh_gia', 0).order('id', desc=True).limit(100).execute()
        ratings = [item['danh_gia'] for item in rating_response.data]
        avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0
        
        # Recent users - lấy số lượng từ records_limit
        users = []
        try:
            users_response = supabase.table('taikhoan').select('id, taikhoan').order('id', desc=True).limit(records_limit).execute()
            
            # Sử dụng truy vấn gộp để lấy số lượng nhận diện cho mỗi người dùng
            if users_response.data:
                user_ids = [user['id'] for user in users_response.data]
                
                for user in users_response.data:
                    # Chỉ đếm số lượng có giới hạn cho mỗi người dùng
                    user_recognitions = supabase.table('lichsunhandien').select('id', count='estimated').eq('user_id', user['id']).limit(100).execute()
                    count = user_recognitions.count if hasattr(user_recognitions, 'count') else len(user_recognitions.data)
                    
                    users.append({
                        'id': user['id'],
                        'taikhoan': user['taikhoan'],
                        'ngay_dang_ky': 'N/A',  # Would need to add this field to your database
                        'luot_nhan_dien': count
                    })
        except Exception as e:
            current_app.logger.error(f"Error fetching users: {str(e)}")
        
        # Recent recognition history - lấy số lượng từ records_limit
        recognition_history = []
        try:
            history_response = supabase.table('lichsunhandien').select('id, user_id, ten_san_pham, do_chinh_xac, thoi_gian').order('thoi_gian', desc=True).limit(records_limit).execute()
            
            # Sử dụng cache để tránh truy vấn lặp lại thông tin người dùng
            user_cache = {}
            
            for record in history_response.data:
                user_id_record = record['user_id']
                
                # Sử dụng cache để tránh truy vấn lặp lại thông tin người dùng
                if user_id_record not in user_cache:
                    user_response = supabase.table('taikhoan').select('taikhoan').eq('id', user_id_record).limit(1).execute()
                    user_cache[user_id_record] = user_response.data[0]['taikhoan'] if user_response.data else 'Unknown'
                
                username_record = user_cache[user_id_record]
                
                # Xử lý dữ liệu an toàn
                try:
                    recognition_history.append({
                        'id': record['id'],
                        'user_name': username_record,
                        'ten_san_pham': record['ten_san_pham'],
                        'do_chinh_xac': round(record['do_chinh_xac'] * 100, 1),
                        'thoi_gian': record['thoi_gian']
                    })
                except Exception as e:
                    current_app.logger.error(f"Error processing history record: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Error fetching recognition history: {str(e)}")
        
        # System logs (giả lập dữ liệu)
        system_logs = []
        
        # Get user avatar
        avatar_url = url_for('static', filename='assets/img/avaters/avatar2.png', _external=True)
        try:
            avatar_response = supabase.table('taikhoan').select('Avarta').eq('id', user_id).limit(1).execute()
            if avatar_response.data and avatar_response.data[0]['Avarta']:
                avatar_url = avatar_response.data[0]['Avarta']
        except Exception as e:
            current_app.logger.error(f"Error fetching user avatar: {str(e)}")
        
        return render_template('admin/dashboard.html', 
                            username=username,
                            avatar_url=avatar_url,
                            total_users=total_users,
                            total_recognitions=total_recognitions,
                            success_rate=success_rate,
                            avg_rating=avg_rating,
                            users=users,
                            recognition_history=recognition_history,
                            system_logs=system_logs)
                            
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {str(e)}")
        flash(f"Có lỗi xảy ra khi tải dữ liệu: {str(e)}", 'error')
        return render_template('admin/dashboard.html', 
                            username=session.get('username'),
                            total_users=0,
                            total_recognitions=0,
                            success_rate=0,
                            avg_rating=0,
                            users=[],
                            recognition_history=[],
                            system_logs=[])

@admin_bp.route("/admin/cache-management", methods=["GET"])
@admin_required
def cache_management():
    user_id = session.get('user_id')
    username = session.get('username')
    
    # Get user avatar
    supabase = get_supabase_client()
    avatar_response = supabase.table('taikhoan').select('Avarta').eq('id', user_id).execute()
    avatar_url = avatar_response.data[0]['Avarta'] if avatar_response.data and avatar_response.data[0]['Avarta'] else url_for('static', filename='assets/img/avatar-default.jpg', _external=True)
    
    return render_template('admin/cache_management.html', username=username, avatar_url=avatar_url)

@admin_bp.route("/admin/clear-cache", methods=["POST"])
@admin_required
def clear_cache():
    cache_type = request.form.get('cache_type', 'all')
    
    # Implement cache clearing logic based on cache_type
    # This is a placeholder and would need to be implemented based on your caching strategy
    
    flash(f"Đã xóa cache: {cache_type}", "success")
    return redirect(url_for('admin.cache_management'))

@admin_bp.route("/admin/users", methods=["GET"])
@admin_required
def user_management():
    user_id = session.get('user_id')
    username = session.get('username')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search_query = request.args.get('search', '')

    supabase = get_supabase_client()
    
    try:
        # Get user avatar
        avatar_response = supabase.table('taikhoan').select('Avarta').eq('id', user_id).limit(1).execute()
        avatar_url = avatar_response.data[0]['Avarta'] if avatar_response.data and avatar_response.data[0]['Avarta'] else url_for('static', filename='assets/img/avatar-default.jpg', _external=True)
        
        # Build query
        query = supabase.table('taikhoan').select('id', count='estimated')
        count_query = query
        
        if search_query:
            query = query.ilike('taikhoan', f'%{search_query}%')
            count_query = count_query.ilike('taikhoan', f'%{search_query}%')
            
        # Get count with limit to avoid timeout
        try:
            count_response = count_query.limit(1000).execute()
            total_users = count_response.count if hasattr(count_response, 'count') else len(count_response.data)
        except Exception as e:
            current_app.logger.error(f"Error counting users: {str(e)}")
            total_users = 100  # Default value if count fails
        
        total_pages = max(1, (total_users + per_page - 1) // per_page)
        
        # Ensure page is within valid range
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages
        
        # Get paginated results
        from_range = (page - 1) * per_page
        to_range = from_range + per_page - 1
        
        # Fetch data with full fields needed
        users_response = supabase.table('taikhoan').select('id, taikhoan, Avarta, is_admin').range(from_range, to_range).order('id').execute()
        users = users_response.data
        
        return render_template('admin/user_management.html', 
                            username=username,
                            avatar_url=avatar_url,
                            users=users,
                            total_users=total_users,
                            page=page,
                            total_pages=total_pages,
                            search_query=search_query)
                            
    except Exception as e:
        current_app.logger.error(f"User management error: {str(e)}")
        flash(f"Có lỗi xảy ra khi tải dữ liệu người dùng: {str(e)}", 'error')
        return render_template('admin/user_management.html', 
                            username=username,
                            avatar_url=url_for('static', filename='assets/img/avatar-default.jpg', _external=True),
                            users=[],
                            total_users=0,
                            page=page,
                            total_pages=0,
                            search_query=search_query)

@admin_bp.route("/admin/recognition-history", methods=["GET"])
@admin_required
def recognition_history():
    user_id = session.get('user_id')
    username = session.get('username')
    page = request.args.get('page', 1, type=int)
    per_page = 6
    search_query = request.args.get('search', '')
    confidence = request.args.get('confidence', '')
    date = request.args.get('date', '')
    type_filter = request.args.get('type', '')
    
    supabase = get_supabase_client()
    
    try:
        # Get user avatar
        avatar_response = supabase.table('taikhoan').select('Avarta').eq('id', user_id).limit(1).execute()
        avatar_url = avatar_response.data[0]['Avarta'] if avatar_response.data and avatar_response.data[0]['Avarta'] else url_for('static', filename='assets/img/avatar-default.jpg', _external=True)
        
        # Build query
        query = supabase.table('lichsunhandien').select('id', count='estimated')
        
        # Apply filters
        if search_query:
            query = query.ilike('ten_san_pham', f'%{search_query}%')
            
        if type_filter:
            query = query.eq('loai_nhan_dien', type_filter)
            
        if confidence:
            if confidence == 'high':
                query = query.gte('do_chinh_xac', 0.9)
            elif confidence == 'medium':
                query = query.gte('do_chinh_xac', 0.7).lt('do_chinh_xac', 0.9)
            elif confidence == 'low':
                query = query.lt('do_chinh_xac', 0.7)
                
        if date:
            today = datetime.now()
            if date == 'today':
                start_date = today.strftime('%Y-%m-%d')
                query = query.gte('thoi_gian', f'{start_date}T00:00:00')
            elif date == 'week':
                start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
                query = query.gte('thoi_gian', f'{start_date}T00:00:00')
            elif date == 'month':
                start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
                query = query.gte('thoi_gian', f'{start_date}T00:00:00')
            
        # Get count with limit to avoid timeout
        try:
            count_response = query.limit(1000).execute()
            total_records = count_response.count if hasattr(count_response, 'count') else len(count_response.data)
        except Exception as e:
            current_app.logger.error(f"Error counting records: {str(e)}")
            total_records = 100  # Default value if count fails
            
        total_pages = max(1, (total_records + per_page - 1) // per_page)
        
        # Ensure page is within valid range
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages
        
        # Get paginated results
        from_range = (page - 1) * per_page
        to_range = from_range + per_page - 1
        
        # Fetch actual data with all needed fields
        data_query = supabase.table('lichsunhandien').select('id, user_id, ten_san_pham, do_chinh_xac, thoi_gian, hinh_anh, loai_nhan_dien')
        
        # Apply same filters to data query
        if search_query:
            data_query = data_query.ilike('ten_san_pham', f'%{search_query}%')
        if type_filter:
            data_query = data_query.eq('loai_nhan_dien', type_filter)
        if confidence:
            if confidence == 'high':
                data_query = data_query.gte('do_chinh_xac', 0.9)
            elif confidence == 'medium':
                data_query = data_query.gte('do_chinh_xac', 0.7).lt('do_chinh_xac', 0.9)
            elif confidence == 'low':
                data_query = data_query.lt('do_chinh_xac', 0.7)
        if date:
            today = datetime.now()
            if date == 'today':
                start_date = today.strftime('%Y-%m-%d')
                data_query = data_query.gte('thoi_gian', f'{start_date}T00:00:00')
            elif date == 'week':
                start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
                data_query = data_query.gte('thoi_gian', f'{start_date}T00:00:00')
            elif date == 'month':
                start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
                data_query = data_query.gte('thoi_gian', f'{start_date}T00:00:00')
                
        history_response = data_query.range(from_range, to_range).order('thoi_gian', desc=True).execute()
        history_data = history_response.data if history_response.data else []
        
        # Store user lookups in cache to avoid repeated queries
        user_cache = {}
        history = []
        
        for record in history_data:
            # Get username for each record using cache
            user_id_record = record['user_id']
            
            if user_id_record not in user_cache:
                user_response = supabase.table('taikhoan').select('taikhoan').eq('id', user_id_record).limit(1).execute()
                user_cache[user_id_record] = user_response.data[0]['taikhoan'] if user_response.data else 'Unknown'
            
            username_record = user_cache[user_id_record]
            
            history.append({
                'id': record['id'],
                'user_name': username_record,
                'ten_san_pham': record['ten_san_pham'],
                'do_chinh_xac': round(record['do_chinh_xac'] * 100, 1),
                'thoi_gian': record['thoi_gian'],
                'hinh_anh': record['hinh_anh'],
                'loai_nhan_dien': record['loai_nhan_dien']
            })
        
        return render_template('admin/recognition_history.html', 
                            username=username,
                            avatar_url=avatar_url,
                            history=history,
                            total_records=total_records,
                            page=page,
                            total_pages=total_pages,
                            search_query=search_query)
                            
    except Exception as e:
        current_app.logger.error(f"Recognition history error: {str(e)}")
        flash(f"Có lỗi xảy ra khi tải lịch sử nhận diện: {str(e)}", 'error')
        return render_template('admin/recognition_history.html', 
                            username=username,
                            avatar_url=url_for('static', filename='assets/img/avatar-default.jpg', _external=True),
                            history=[],
                            total_records=0,
                            page=page,
                            total_pages=0,
                            search_query=search_query)

@admin_bp.route("/admin/api/chart-data", methods=["GET"])
@admin_required
def chart_data():
    time_period = request.args.get('period', 'week')
    
    supabase = get_supabase_client()
    today = datetime.now()
    
    try:
        if time_period == 'day':
            # Get data for the last 24 hours by hour
            start_date = today - timedelta(hours=24)
            labels = [f"{hour}:00" for hour in range(24)]
            
            # Single image data
            single_data = [0] * 24
            # Multi image data
            multi_data = [0] * 24
            
            # This is a simplified version - in a real application, you would query 
            # by hour and aggregate the counts in your database
        
        elif time_period == 'week':
            # Get data for the last 7 days
            start_date = today - timedelta(days=7)
            labels = [(today - timedelta(days=i)).strftime('%a') for i in range(6, -1, -1)]
            
            # Placeholder data - in a real application, query your database
            single_data = [12, 19, 3, 5, 2, 3, 9]
            multi_data = [7, 11, 5, 8, 3, 7, 12]
            
        elif time_period == 'month':
            # Get data for the last 30 days by week
            labels = ['Tuần 1', 'Tuần 2', 'Tuần 3', 'Tuần 4']
            
            # Placeholder data
            single_data = [42, 38, 55, 47]
            multi_data = [25, 31, 28, 32]
            
        elif time_period == 'year':
            # Get data for the last 12 months
            labels = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12']
            
            # Placeholder data
            single_data = [100, 120, 150, 170, 160, 190, 210, 200, 180, 160, 170, 190]
            multi_data = [80, 90, 100, 110, 100, 120, 130, 120, 110, 100, 110, 120]
        
        return jsonify({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Nhận diện đơn ảnh',
                    'data': single_data
                },
                {
                    'label': 'Nhận diện đa ảnh',
                    'data': multi_data
                }
            ]
        })
        
    except Exception as e:
        current_app.logger.error(f"Chart data error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route("/admin/settings", methods=["GET"])
@admin_required
def settings():
    try:
        # Lấy thông tin cấu hình hiện tại
        system_config = get_system_config()
        
        # Lấy danh sách mô hình có sẵn
        available_models = get_available_models()
        
        # Get user avatar
        user_id = session.get('user_id')
        username = session.get('username')
        
        supabase = get_supabase_client()
        avatar_response = supabase.table('taikhoan').select('Avarta').eq('id', user_id).execute()
        avatar_url = avatar_response.data[0]['Avarta'] if avatar_response.data and avatar_response.data[0]['Avarta'] else url_for('static', filename='assets/img/avatar-default.jpg', _external=True)
        
        return render_template('admin/settings.html',
                             username=username,
                             avatar_url=avatar_url,
                             available_models=available_models,
                             current_model=system_config.get('model_path', MODEL_SAVE_PATH),
                             img_size=system_config.get('img_size', IMG_SIZE),
                             confidence_threshold=system_config.get('confidence_threshold', CONFIDENCE_THRESHOLD),
                             max_predictions=system_config.get('max_predictions', 5),
                             enable_image_check=system_config.get('enable_image_check', True))
    except Exception as e:
        current_app.logger.error(f"Settings error: {str(e)}")
        flash(f"Có lỗi xảy ra khi tải trang cài đặt: {str(e)}", 'error')
        return render_template('admin/settings.html',
                             username=session.get('username'),
                             avatar_url=url_for('static', filename='assets/img/avatar-default.jpg', _external=True),
                             available_models=[],
                             current_model=MODEL_SAVE_PATH,
                             img_size=IMG_SIZE,
                             confidence_threshold=CONFIDENCE_THRESHOLD,
                             max_predictions=5,
                             enable_image_check=True)

@admin_bp.route("/admin/save-settings", methods=["POST"])
@admin_required
def save_settings():
    try:
        model_path = request.form.get('model_path', MODEL_SAVE_PATH)
        img_width = int(request.form.get('img_width', IMG_SIZE[0]))
        img_height = int(request.form.get('img_height', IMG_SIZE[1]))
        confidence_threshold = float(request.form.get('confidence_threshold', 50)) / 100.0 # Convert from percentage
        max_predictions = int(request.form.get('max_predictions', 5))
        enable_image_check = 'enable_image_check' in request.form
        
        # Validate inputs
        if img_width < 32 or img_width > 512 or img_height < 32 or img_height > 512:
            flash('Kích thước ảnh phải nằm trong khoảng 32x32 đến 512x512', 'error')
            return redirect(url_for('admin.settings'))
        
        if confidence_threshold < 0.01 or confidence_threshold > 0.99:
            flash('Ngưỡng độ tin cậy phải nằm trong khoảng 1% đến 99%', 'error')
            return redirect(url_for('admin.settings'))
        
        if max_predictions < 1 or max_predictions > 10:
            flash('Số lượng kết quả tối đa phải nằm trong khoảng 1 đến 10', 'error')
            return redirect(url_for('admin.settings'))
        
        # Tạo đối tượng cấu hình mới
        new_config = {
            'model_path': model_path,
            'img_size': (img_width, img_height),
            'confidence_threshold': confidence_threshold,
            'max_predictions': max_predictions,
            'enable_image_check': enable_image_check,
            'last_updated': datetime.now().isoformat()
        }
        
        # Lưu cấu hình mới
        save_system_config(new_config)
        
        # Tải lại mô hình (thực hiện trong một tiến trình riêng hoặc thread để không block request)
        try:
            # Import here to avoid circular imports
            from routers.predict import reload_model
            reload_model()
        except Exception as model_error:
            current_app.logger.error(f"Error reloading model: {str(model_error)}")
            flash(f"Đã lưu cài đặt nhưng có lỗi khi tải lại mô hình: {str(model_error)}", 'warning')
            return redirect(url_for('admin.settings'))
        
        flash('Đã lưu cài đặt thành công', 'success')
        return redirect(url_for('admin.settings'))
        
    except Exception as e:
        current_app.logger.error(f"Save settings error: {str(e)}")
        flash(f"Có lỗi xảy ra khi lưu cài đặt: {str(e)}", 'error')
        return redirect(url_for('admin.settings'))

# Helper functions
def get_system_config():
    """Lấy cấu hình hệ thống từ file config hoặc database"""
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'system_config.json')
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            current_app.logger.error(f"Error loading system config: {str(e)}")
    
    # Return default config if file doesn't exist or can't be loaded
    return {
        'model_path': MODEL_SAVE_PATH,
        'img_size': IMG_SIZE,
        'confidence_threshold': CONFIDENCE_THRESHOLD,
        'max_predictions': 5,
        'enable_image_check': True
    }

def save_system_config(config):
    """Lưu cấu hình hệ thống vào file config hoặc database"""
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'system_config.json')
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        current_app.logger.error(f"Error saving system config: {str(e)}")
        raise e

def get_available_models():
    """Quét thư mục saved_model để lấy danh sách các mô hình có sẵn"""
    models = []
    model_dir = os.path.dirname(MODEL_SAVE_PATH)
    
    try:
        for filename in os.listdir(model_dir):
            if filename.endswith('.h5'):
                file_path = os.path.join(model_dir, filename)
                file_stats = os.stat(file_path)
                
                # Trích xuất thông tin mô hình
                model_info = {
                    'name': filename,
                    'path': file_path,
                    'size': f"{file_stats.st_size / (1024 * 1024):.1f} MB",
                    'created_at': datetime.fromtimestamp(file_stats.st_ctime).strftime('%d/%m/%Y'),
                    'img_size': '128x128'  # Default
                }
                
                # Xác định kích thước ảnh dựa trên tên mô hình
                if 'mobilenetv2' in filename.lower():
                    model_info['img_size'] = '224x224'
                    model_info['description'] = 'MobileNetV2 - Mô hình nhẹ, hiệu năng cao, phù hợp với ứng dụng di động'
                elif 'efficientnet' in filename.lower():
                    model_info['img_size'] = '224x224' 
                    model_info['description'] = 'EfficientNet - Cân bằng giữa độ chính xác và hiệu suất'
                elif 'resnet' in filename.lower():
                    model_info['img_size'] = '224x224'
                    model_info['description'] = 'ResNet - Mạng neural sâu với độ chính xác cao'
                elif 'vgg' in filename.lower():
                    model_info['img_size'] = '224x224'
                    model_info['description'] = 'VGG - Kiến trúc cổ điển, ổn định với nhiều loại dữ liệu'
                else:
                    if '128' in filename:
                        model_info['img_size'] = '128x128'
                    elif '100' in filename:
                        model_info['img_size'] = '100x100'
                    elif '224' in filename:
                        model_info['img_size'] = '224x224'
                    model_info['description'] = 'Mô hình tùy chỉnh'
                    
                models.append(model_info)
        
        # Sắp xếp theo thời gian tạo mới nhất
        models.sort(key=lambda x: x['created_at'], reverse=True)
        
        return models
    except Exception as e:
        current_app.logger.error(f"Error getting available models: {str(e)}")
        return []