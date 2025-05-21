from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_VISION_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE, TIMEOUT
from services.supabase_service import get_supabase_client
from datetime import datetime
import json
import base64

client = OpenAI(api_key=OPENAI_API_KEY)

def check_image_content(image_base64):
    """Kiểm tra ảnh có phải hoa quả/rau củ, tối ưu hóa token và chi phí."""
    try:
        # Bỏ phần prefix "data:image/..." nếu có
        if "base64," in image_base64:
            image_base64 = image_base64.split("base64,")[1]
        
        # Tạo client OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Gửi yêu cầu với prompt đơn giản hơn
        response = client.chat.completions.create(
            model= OPENAI_VISION_MODEL,  # Sử dụng model hỗ trợ vision
            messages=[
                {
                    "role": "system",
                    "content": "Nhiệm vụ của bạn là xác định ảnh có chứa hoa quả, rau củ, hoặc nông sản hay không. Chỉ trả lời YES hoặc NO."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "Đây có phải ảnh hoa quả/rau củ/nông sản không? Chỉ trả lời YES hoặc NO."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=10  # Giảm max_tokens xuống, chỉ cần đủ cho YES/NO
        )
        
        answer = response.choices[0].message.content.strip().upper()
        
        # Kiểm tra kết quả
        if "YES" in answer:
            return True, ""
        else:
            return False, ""
            
    except Exception as e:
        print(f"Lỗi khi kiểm tra nội dung ảnh: {str(e)}")
        # Khi có lỗi, mặc định từ chối ảnh để an toàn
        return False, ""

def generate_recipes_with_openai(fruit_type, num_recipes=3):
    try:
        supabase = get_supabase_client()
        existing_recipes = supabase.table('cong_thuc_ai').select('*').eq('loai_hoa_qua', fruit_type).execute()
        
        if existing_recipes.data and len(existing_recipes.data) > 0:
            recipe_data = existing_recipes.data[0]
            supabase.table('cong_thuc_ai').update({'su_dung_gan_nhat': datetime.now().isoformat()}).eq('id', recipe_data['id']).execute()
            return recipe_data['noi_dung'], True, "Tạo bởi AI (cache)"
        
        prompt = f"""Tạo {num_recipes} công thức món ăn đơn giản từ {fruit_type}, với 3 mức độ khó khác nhau:
        - 1 món Dễ
        - 1 món Trung bình
        - 1 món Khó
        
        Cho mỗi công thức, hãy bao gồm:
        - Tên món (ngắn gọn)
        - Độ khó (chỉ rõ là Dễ/Trung bình/Khó)
        - Thời gian (phút)
        - 3-5 nguyên liệu chính
        - 3-4 bước nấu đơn giản
        
        Định dạng JSON:
        [
          {{
            "ten_mon": "Tên món",
            "do_kho": "Dễ/Trung bình/Khó",
            "thoi_gian_nau": 20,
            "nguyen_lieu": ["Nguyên liệu 1", "Nguyên liệu 2", "..."],
            "cach_lam": "Bước 1: ...\nBước 2: ...\n..."
          }}
        ]
        Chỉ trả về JSON."""

        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Bạn là đầu bếp tạo công thức đơn giản. Chỉ trả về JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS,
                timeout=TIMEOUT
            )
            
            recipes_text = response.choices[0].message.content.strip()
            recipes_text = recipes_text.replace('```json', '').replace('```', '').strip()
            
            try:
                recipes = json.loads(recipes_text)
                formatted_recipes = []
                for i, recipe in enumerate(recipes):
                    formatted_recipe = {
                        "id": f"ai_{i}",
                        "ten_mon": recipe.get("ten_mon", f"Món từ {fruit_type}"),
                        "do_kho": recipe.get("do_kho", "Dễ"),
                        "thoi_gian_nau": recipe.get("thoi_gian_nau", 20),
                        "nguyen_lieu": recipe.get("nguyen_lieu", []),
                        "cach_lam": recipe.get("cach_lam", ""),
                        "loai_hoa_qua": fruit_type,
                    }
                    formatted_recipes.append(formatted_recipe)
                
                supabase.table('cong_thuc_ai').insert({
                    'loai_hoa_qua': fruit_type,
                    'noi_dung': formatted_recipes, 
                    'nguon': 'openai'
                }).execute()
                    
                return formatted_recipes, True, "Tạo bởi AI"
                
            except json.JSONDecodeError:
                return None, False, "Không thể xử lý phản hồi từ AI"
            
        except Exception as api_error:
            print(f"Lỗi API OpenAI: {str(api_error)}")
            return None, False, "API OpenAI không khả dụng"
            
    except Exception as e:
        print(f"Lỗi khi tạo công thức: {str(e)}")
        return None, False, "Sử dụng công thức mẫu"
