from flask import Blueprint, request, jsonify
from services.openai_service import generate_recipes_with_openai
from utils.recipe_utils import create_sample_recipes
from flask import current_app

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route("/get-recipes", methods=["GET"])
def get_recipes():
    fruit_type = request.args.get("fruit_type", "")
    use_ai = request.args.get("use_ai", "false").lower() == "true"
    
    if not fruit_type:
        return jsonify({"success": False, "error": "Không cung cấp loại trái cây"}), 400
    
    try:
        if use_ai:
            recipes, success, message = generate_recipes_with_openai(fruit_type)
            source = "openai" if success else "sample"
        else:
            recipes = create_sample_recipes(fruit_type)
            success = True
            message = "Công thức mẫu"
            source = "sample"
        
        return jsonify({
            "success": success,
            "recipes": recipes,
            "message": message,
            "source": source
        })
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        current_app.logger.error(f"Lỗi khi lấy công thức: {e}")
        current_app.logger.error(f"Chi tiết lỗi: {error_detail}")
        
        try:
            fallback_recipes = create_sample_recipes(fruit_type)
            return jsonify({
                "success": True,
                "recipes": fallback_recipes,
                "message": f"Sử dụng công thức mẫu (gặp lỗi: {str(e)})",
                "source": "sample"
            })
        except:
            return jsonify({
                "success": False,
                "error": str(e),
                "message": "Không thể tạo công thức, vui lòng thử lại sau"
            }), 500
