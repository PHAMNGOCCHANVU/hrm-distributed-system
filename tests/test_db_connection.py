import psycopg2

sites = [
    {
        'name': 'site_dn (Đà Nẵng - Shard DN)',
        'host': 'localhost',
        'port': 5434,
        'dbname': 'qlns_dn',
        'user': 'postgres',
        'password': 'PasswordDN_123',
        'query': 'SELECT MaNV, HoTen, MaPB, MaCN, TrangThai FROM NhanVien;'
    },
    {
        'name': 'site_hcm (TP. Hồ Chí Minh - Shard HCM)',
        'host': 'localhost',
        'port': 5433,
        'dbname': 'qlns_hcm',
        'user': 'postgres',
        'password': 'PasswordHCM_123',
        'query': 'SELECT MaNV, HoTen, MaPB, MaCN, TrangThai FROM NhanVien;'
    },
    {
        'name': 'site_hn (Hà Nội - Shard HN cục bộ)',
        'host': 'localhost',
        'port': 5431,
        'dbname': 'qlns_hn',
        'user': 'postgres',
        'password': 'PasswordHN_123',
        'query': 'SELECT MaNV, HoTen, MaPB, MaCN, TrangThai FROM NhanVien;'
    },
    {
        'name': 'site_hn (Coordinator - Global View: v_HoSoNhanSu_ToanDien qua postgres_fdw)',
        'host': 'localhost',
        'port': 5431,
        'dbname': 'qlns_hn',
        'user': 'postgres',
        'password': 'PasswordHN_123',
        'query': 'SELECT MaNV, HoTen, TenPhongBan, ChucVuHienTai, ChiNhanh, LuongThucLinh, XepLoai_KPI_Q1 FROM v_HoSoNhanSu_ToanDien;'
    }
]

print("=" * 70)
print("KIỂM TRA KẾT NỐI VÀ TRUY VẤN CƠ SỞ DỮ LIỆU PHÂN TÁN (SPACEX HRM)")
print("=" * 70)

all_success = True
results = []

for site in sites:
    print(f"\n[*] Đang kết nối tới: {site['name']} (Port {site['port']})...")
    try:
        conn = psycopg2.connect(
            host=site['host'],
            port=site['port'],
            dbname=site['dbname'],
            user=site['user'],
            password=site['password'],
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute(site['query'])
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        print(f"   [+] TRẠNG THÁI: KẾT NỐI VÀ TRUY VẤN THÀNH CÔNG!")
        print(f"   [+] Các cột: {', '.join(col_names)}")
        print(f"   [+] Số bản ghi lấy được: {len(rows)}")
        for r in rows:
            print(f"       -> {r}")
        cursor.close()
        conn.close()
        results.append((site['name'], True, len(rows)))
    except Exception as e:
        all_success = False
        print(f"   [-] TRẠNG THÁI: THẤT BẠI!")
        print(f"   [-] Chi tiết lỗi: {e}")
        results.append((site['name'], False, str(e)))

print("\n" + "=" * 70)
print("BẢNG TỔNG HỢP KẾT QUẢ KIỂM TRA")
print("=" * 70)
for name, status, detail in results:
    status_str = "THÀNH CÔNG" if status else "THẤT BẠI"
    info = f"{detail} bản ghi" if status else f"Lỗi: {detail}"
    print(f"- {name:<60}: [{status_str}] ({info})")

if all_success:
    print("\n=> KẾT LUẬN: TOÀN BỘ CỤM CƠ SỞ DỮ LIỆU PHÂN TÁN KẾT NỐI VÀ TRUY VẤN THÀNH CÔNG 100%!")
else:
    print("\n=> KẾT LUẬN: CÓ NODE GẶP LỖI KẾT NỐI HOẶC CHƯA NẠP ĐẦY ĐỦ VIEW/DATA!")
