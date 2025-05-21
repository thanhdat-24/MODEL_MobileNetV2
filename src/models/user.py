from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, taikhoan, Avarta=None, is_admin=False):
        self.id = id
        self.taikhoan = taikhoan
        self.Avarta = Avarta
        self.is_admin = is_admin
    
    def __repr__(self):
        return f"<User {self.taikhoan}>"
    
    def get_id(self):
        return str(self.id) 