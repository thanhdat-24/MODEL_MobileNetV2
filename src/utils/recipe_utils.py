import json

def create_sample_recipes(fruit_type):
    """Tạo một số công thức mẫu đơn giản cho loại hoa quả"""
    recipes = []
    
    # Công thức 1: Sinh tố (Dễ)
    recipes.append({
        "id": 1,
        "ten_mon": f"Sinh tố {fruit_type}",
        "nguyen_lieu": json.dumps([
            f"2 quả {fruit_type}",
            "200ml sữa",
            "1 muỗng mật ong",
            "Đá"
        ]),
        "cach_lam": f"1. Gọt vỏ và cắt {fruit_type}\n2. Cho tất cả vào máy xay\n3. Xay nhuyễn và thưởng thức",
        "loai_hoa_qua": fruit_type,
        "thoi_gian_nau": 5,
        "do_kho": "Dễ",
        "luot_thich": 0
    })
    
    # Công thức 2: Salad (Trung bình)
    recipes.append({
        "id": 2,
        "ten_mon": f"Salad {fruit_type}",
        "nguyen_lieu": json.dumps([
            f"1 quả {fruit_type}",
            "Rau xà lách",
            "Dầu olive",
            "Chanh",
            "Hạt điều"
        ]),
        "cach_lam": f"1. Rửa sạch rau và cắt nhỏ\n2. Cắt {fruit_type} thành miếng vừa ăn\n3. Trộn đều với dầu olive và nước cốt chanh\n4. Rắc hạt điều lên trên và thưởng thức",
        "loai_hoa_qua": fruit_type,
        "thoi_gian_nau": 10,
        "do_kho": "Trung bình",
        "luot_thich": 0
    })
    
    # Công thức 3: Bánh nướng (Khó)
    recipes.append({
        "id": 3,
        "ten_mon": f"Bánh nướng {fruit_type}",
        "nguyen_lieu": json.dumps([
            f"3 quả {fruit_type}",
            "200g bột mì",
            "100g đường",
            "2 quả trứng gà",
            "100g bơ",
            "1 muỗng cà phê bột nở"
        ]),
        "cach_lam": f"1. Trộn bột mì, đường và bột nở\n2. Đánh tan trứng và bơ, trộn với hỗn hợp bột\n3. Cắt {fruit_type} thành lát mỏng và xếp lên trên bột\n4. Nướng ở 180°C trong 30 phút",
        "loai_hoa_qua": fruit_type,
        "thoi_gian_nau": 45,
        "do_kho": "Khó",
        "luot_thich": 0
    })
    
    return recipes
