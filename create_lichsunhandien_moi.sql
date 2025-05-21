create table taikhoan (
  id int8 primary key generated always as identity,
  taikhoan text,
	matkhau text,
	Avarta text,
  is_admin boolean default false
);
-- Chạy query này trong Supabase SQL Editor để tạo bảng lịch sử
create table lichsunhandien (
  id int8 primary key generated always as identity,
  user_id int8 references taikhoan(id),
  hinh_anh text,  -- URL hoặc base64 của hình ảnh
  ket_qua text,   -- JSON chứa kết quả nhận diện
  ten_san_pham text, -- Tên sản phẩm được nhận diện
  do_chinh_xac float, -- Độ chính xác
  thoi_gian timestamp default now(),
  nhan_dien_thanh_cong boolean,
  loai_nhan_dien text DEFAULT 'don_anh',
  danh_gia int DEFAULT 0 -- Trường đánh giá sao (0-5)
);
-- Tạo bảng nhóm kết quả cho chế độ đa ảnh
CREATE TABLE nhom_ket_qua (
  id int8 primary key generated always as identity,
  user_id int8 references taikhoan(id),
  hinh_anh_dai_dien text,  -- URL hoặc base64 của hình ảnh đại diện
  ten_nhom text, -- Tên loại sản phẩm của nhóm
  so_luong int, -- Số lượng hình ảnh trong nhóm
  do_chinh_xac float, -- Độ chính xác trung bình
  thoi_gian timestamp default now(),
  nhan_dien_thanh_cong boolean
);

-- Tạo bảng trung gian để liên kết kết quả đơn lẻ với nhóm
CREATE TABLE ket_qua_nhom (
  id int8 primary key generated always as identity,
  nhom_id int8 references nhom_ket_qua(id),
  lichsu_id int8 references lichsunhandien(id),
  created_at timestamp default now()
);
CREATE TABLE cong_thuc_ai (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  loai_hoa_qua TEXT NOT NULL,
  noi_dung JSONB NOT NULL,
  thoi_gian TIMESTAMP DEFAULT NOW(),
  nguon TEXT DEFAULT 'openai',
  su_dung_gan_nhat TIMESTAMP DEFAULT NOW()
);