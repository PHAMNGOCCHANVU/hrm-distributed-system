-- 05_demo_explain.sql
-- Các câu truy vấn kiểm thử EXPLAIN ANALYZE cho báo cáo

-- 1. Truy vấn hợp nhất toàn diện 3 dạng dữ liệu trên toàn tập đoàn
SELECT 
    MaNV, HoTen, ChiNhanh, ChucVuHienTai, LuongThucLinh, XepLoai_KPI_Q1, URL_AnhDaiDien 
FROM v_HoSoNhanSu_ToanDien;

-- 2. Đo lường cây thực thi phân tán (minh chứng đẩy điều kiện lọc xuống các Node từ xa)
EXPLAIN ANALYZE
SELECT MaNV, HoTen, ChiNhanh, XepLoai_KPI_Q1
FROM v_HoSoNhanSu_ToanDien
WHERE ChiNhanh = 'HCM' AND XepLoai_KPI_Q1 = 'A';
