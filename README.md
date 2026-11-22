# SpaceX HRM - Hệ Thống Quản Trị Nhân Sự & Lương Phân Tán Đa Chi Nhánh

> **Dự án**: Hệ thống Quản trị Nhân sự, Chấm công, Tính lương và Hồ sơ Năng lực Phân tán (SpaceX HRM Distributed System).  
> **Kiến trúc**: Micro-services / RESTful API (FastAPI) + Single Page Application (React 18 + Vite + Tailwind CSS + Ant Design) kết hợp Cụm Cơ sở Dữ liệu Phân tán (PostgreSQL `postgres_fdw`, `JSONB`) và MinIO Object Storage (S3-compatible).

---

## 1. Kiến trúc Tổng thể Hệ thống

Hệ thống được thiết kế theo mô hình **tách biệt hoàn toàn giữa Frontend (SPA) và Backend (RESTful API dạng Smart Data Orchestrator)**, vận hành trên cụm hạ tầng Docker gồm 4 dịch vụ độc lập:

* **Tầng Frontend (SPA):** Giao tiếp qua chuẩn RESTful API (JSON & Multipart Form-Data). Đạt **Tính trong suốt phân mảnh (Fragmentation Transparency)**: Dùng chung một giao diện Web duy nhất cho cả 3 miền, điều phối nghiệp vụ qua cơ chế **JWT Role & Department Guard**.
* **Tầng Backend (FastAPI Smart Orchestrator):** 
  * Quản lý đồng thời 3 Connection Pools tới 3 node PostgreSQL và 1 S3 Client tới MinIO.
  * **Định tuyến thông minh (Distributed Data Router):** Đọc toàn cục qua Coordinator `site_hn` (`postgres_fdw` + Global Views), đọc cục bộ tối ưu tại `site_dn`/`site_hcm`, và ghi phân mảnh chuẩn xác theo thuộc tính `MaCN`.
  * **Điều phối đa mô hình (Multi-Model Orchestrator):** Đồng bộ dữ liệu Quan hệ (SQL), Bán cấu trúc (`JSONB` skills/KPI) và Phi cấu trúc (MinIO S3) kèm cơ chế đền bù 2 pha (Compensating Delete).
* **Tầng CSDL Phân tán & Lưu trữ (Docker Infrastructure):**
  * **`site_hn` (Port 5431):** Coordinator Node (chứa Global Views) kiêm lưu trữ phân mảnh Hà Nội (db: `qlns_hn`).
  * **`site_dn` (Port 5434):** Lưu trữ phân mảnh Đà Nẵng (db: `qlns_dn`).
  * **`site_hcm` (Port 5433):** Lưu trữ phân mảnh TP. Hồ Chí Minh (db: `qlns_hcm`).
  * **`minio_server` (Port 9000 S3 API / 9001 Web Console):** Lưu trữ đối tượng phi cấu trúc (ảnh đại diện, scan CV PDF, hợp đồng) trong bucket `nhansu-bucket`.

---

## 2. Cấu trúc Thư mục Dự án

```text
spacex-hrm-distributed/
├── docker-compose.yml                 # Khởi chạy cụm 3 container PostgreSQL + MinIO
├── .env.example                       # Mẫu cấu hình biến môi trường
├── .gitignore                         # Danh sách loại trừ Git
├── README.md                          # Tài liệu hướng dẫn cài đặt & vận hành hệ thống
│
├── database/                          # TẦNG CSDL & HẠ TẦNG PHÂN TÁN
│   ├── scripts/
│   │   ├── 01_site_dn_init.sql        # Phân mảnh ĐN: CHECK (MaCN='DN'), Index, data mẫu
│   │   ├── 02_site_hcm_init.sql       # Phân mảnh HCM: CHECK (MaCN='HCM'), Index, data mẫu
│   │   ├── 03_site_hn_init.sql        # Phân mảnh HN: Cấu hình postgres_fdw, Global Views, data mẫu
│   │   ├── 04_site_hn_fdw_views.sql   # Kịch bản FDW & Global Views (v_HoSoNhanSu_ToanDien)
│   │   └── 05_demo_explain.sql        # Kịch bản kiểm thử EXPLAIN ANALYZE minh chứng phân tán
│   └── seed_minio/
│       ├── upload_minio.py            # Script tạo bucket, gán Public Policy và đẩy file lên MinIO
│       ├── images/                    # Ảnh đại diện mẫu (NV_HN_01.jpg, NV_DN_01.jpg, ...)
│       └── cv_docs/                   # File scan CV PDF mẫu (NV_HN_01_CV.pdf, ...)
│
├── backend/                           # TẦNG BACKEND (Python + FastAPI)
│   ├── requirements.txt               # fastapi, uvicorn, psycopg2-binary, minio, pyjwt,...
│   ├── .env                           # Cấu hình kết nối tới 3 DB (5431, 5434, 5433) và MinIO (9000)
│   └── app/
│       ├── main.py                    # Khởi tạo FastAPI, CORS và đăng ký Router
│       ├── core/                      # [config.py, db_router.py, minio_client.py, security.py]
│       ├── schemas/                   # [auth.py, employee.py, payroll.py, catalog.py]
│       ├── repositories/              # [employee_repo.py, payroll_repo.py, catalog_repo.py, health_repo.py]
│       ├── services/                  # [auth_service.py, employee_service.py, payroll_service.py, system_service.py]
│       └── api/                       # [deps.py, routes: auth, employees, payroll, catalogs, system]
│
├── frontend/                          # TẦNG FRONTEND (React 18 + Vite + Tailwind + Ant Design)
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx / App.jsx
│       ├── api/                       # [axiosClient.js, employeeApi.js, payrollApi.js, systemApi.js]
│       ├── context/                   # [AuthContext.jsx] Quản lý state người dùng toàn ứng dụng
│       ├── routes/                    # [AppRoutes.jsx, ProtectedRoute.jsx] Route Guard theo RBAC
│       ├── layouts/                   # [MainLayout.jsx] Sidebar/Header điều hướng động theo quyền
│       ├── components/                # [EmployeeTable.jsx, JsonProfileForm.jsx, FileUploader.jsx, SiteStatusBadge.jsx]
│       └── pages/                     # [auth, director, hr, finance, employee, monitor]
│
└── docs/                              # TÀI LIỆU BÁO CÁO & ĐẶC TẢ
    ├── architect/                     # [system-design.md, source-code.md]
    ├── specs/                         # [business-specs.md] Đặc tả RBAC, Data Masking & API mapping
    ├── diagrams/                      # Sơ đồ kiến trúc, ERD, Sequence diagrams
    └── screenshots/                   # Ảnh chụp EXPLAIN ANALYZE, MinIO và giao diện Web
```

---

## 3. Hướng dẫn Cài đặt & Thứ tự Chạy Hệ thống

### Bước 1: Khởi chạy Hạ tầng Docker
Tại thư mục gốc dự án, khởi chạy cụm 3 container PostgreSQL và MinIO:
```powershell
docker compose up -d
```
Kiểm tra trạng thái container đang hoạt động (`docker compose ps`):
- `site_hn`: Cổng `5431->5432`
- `site_dn`: Cổng `5434->5432`
- `site_hcm`: Cổng `5433->5432`
- `minio_server`: Cổng `9000` (API) và `9001` (Web Console)

---

### Bước 2: Nạp Dữ liệu Khởi tạo CSDL Phân tán (Thứ tự bắt buộc)

> **Lưu ý quan trọng**: Phải khởi tạo 2 node thành viên (`site_dn`, `site_hcm`) trước để tạo `user` từ xa và bảng dữ liệu, sau đó mới khởi tạo node điều phối (`site_hn`) để cấu hình `postgres_fdw` liên kết sang 2 site kia.

1. **Khởi tạo Site Đà Nẵng (Port 5434)**:
   ```powershell
   docker exec -i site_dn psql -U postgres -d qlns_dn < database/scripts/01_site_dn_init.sql
   ```
2. **Khởi tạo Site TP. Hồ Chí Minh (Port 5433)**:
   ```powershell
   docker exec -i site_hcm psql -U postgres -d qlns_hcm < database/scripts/02_site_hcm_init.sql
   ```
3. **Khởi tạo Site Hà Nội & Cấu hình FDW Global Views (Port 5431)**:
   ```powershell
   docker exec -i site_hn psql -U postgres -d qlns_hn < database/scripts/03_site_hn_init.sql
   ```
4. *(Tùy chọn) Kiểm tra tính năng đẩy điều kiện lọc phân tán*:
   ```powershell
   docker exec -i site_hn psql -U postgres -d qlns_hn < database/scripts/05_demo_explain.sql
   ```

---

### Bước 3: Nạp Dữ liệu Mẫu lên MinIO Object Storage
Cài đặt thư viện và chạy script đẩy ảnh đại diện cùng scan CV mẫu lên MinIO bucket:
```powershell
python database/seed_minio/upload_minio.py
```
* Sau khi chạy, kiểm tra tại Web Console: **http://localhost:9001** (User: `admin_minio` / Pass: `PasswordMinio_123`).
* Toàn bộ ảnh sẽ truy cập được trực tiếp qua URL công khai: `http://localhost:9000/nhansu-bucket/avatars/...`

---

### Bước 4: Cài đặt và Khởi chạy Backend (FastAPI)
1. Di chuyển vào thư mục `backend`:
   ```powershell
   cd backend
   ```
2. Kích hoạt môi trường ảo:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   *(Nếu chưa cài thư viện: `pip install -r requirements.txt`)*
3. Cấu hình file `backend/.env` (nếu chưa có, sao chép từ `.env.example`):
   ```env
   DB_HN_HOST=localhost
   DB_HN_PORT=5431
   DB_HN_NAME=qlns_hn
   DB_HN_USER=postgres
   DB_HN_PASS=PasswordHN_123

   DB_DN_HOST=localhost
   DB_DN_PORT=5434
   DB_DN_NAME=qlns_dn
   DB_DN_USER=postgres
   DB_DN_PASS=PasswordDN_123

   DB_HCM_HOST=localhost
   DB_HCM_PORT=5433
   DB_HCM_NAME=qlns_hcm
   DB_HCM_USER=postgres
   DB_HCM_PASS=PasswordHCM_123

   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=admin_minio
   MINIO_SECRET_KEY=PasswordMinio_123
   MINIO_BUCKET=nhansu-bucket
   JWT_SECRET=SpaceX_HRM_SecretKey_2026
   ```
4. Khởi chạy FastAPI Server:

   ```powershell
   cd backend
   .\.venv\Scripts\Activate.ps1
   ```

   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```
   * **API Docs (Swagger UI)**: **[http://localhost:8000/docs](http://localhost:8000/docs)**
   * **ReDoc**: **[http://localhost:8000/redoc](http://localhost:8000/redoc)**

---

### Bước 5: Cài đặt và Khởi chạy Frontend (React + Vite)
1. Mở một terminal mới, di chuyển vào thư mục `frontend`:
   ```powershell
   cd frontend
   ```
2. Cài đặt các gói phụ thuộc (nếu chưa cài):
   ```powershell
   npm install
   ```
3. Khởi chạy máy chủ phát triển Vite:
   ```powershell
   npm run dev
   ```
   * **Ứng dụng Web SPA**: **[http://localhost:3000](http://localhost:3000)**

---

## 4. Danh sách Tài khoản Demo & Phân quyền Truy cập (RBAC)

Hệ thống cung cấp sẵn các tài khoản demo kiểm thử tương ứng từng phân cấp vai trò và phòng ban:

| Tên Đăng Nhập | Mật Khẩu | Mã NV | Họ và Tên | Vai Trò (Role) | Phòng Ban | Chi Nhánh | Phạm Vi Quyền Hạn & Tính Năng Nổi Bật |
| :--- | :---: | :---: | :--- | :--- | :--- | :---: | :--- |
| **`giap_gd`** | `123456` | `NV_HN_01` | Lưu Quang Giáp | **Tổng giám đốc** (CEO) | Quản Trị Trung Tâm | **HN** | **Toàn tập đoàn (3 miền)**: Xem toàn bộ nhân sự, độc quyền phê duyệt/sửa lương mọi nhân viên, xem nhật ký kiểm toán toàn quốc, Dashboard phân tích tổng hợp 3 miền. |
| **`cuong_dn`** | `123456` | `NV_DN_01` | Phạm Văn Cường | **Giám đốc** (Chi nhánh) | Ban Giám Đốc ĐN | **DN** | **Toàn chi nhánh Đà Nẵng**: Xem và cập nhật lương nhân sự thuộc chi nhánh ĐN, quản lý hồ sơ nhân sự ĐN (chặn sửa lương chi nhánh khác). |
| **`linh_hcm`** | `123456` | `NV_HCM_01` | Trần Thị Mỹ Linh | **Giám đốc** (Chi nhánh) | Ban Giám Đốc HCM | **HCM** | **Toàn chi nhánh TP.HCM**: Xem và cập nhật lương nhân sự thuộc chi nhánh HCM, quản lý hồ sơ nhân sự HCM. |
| **`nhansu_truong`** | `123456` | `NV_HN_03` | Nguyễn Văn An | **Trưởng phòng** | Phòng Nhân Sự | **HN** | **Quản lý nhân sự toàn tập đoàn**: Thêm/Sửa hồ sơ, upload ảnh/CV MinIO, cập nhật JSONB skills/KPI. Lương người khác bị Mask (`NULL`), chỉ xem lương của chính mình. |
| **`hoa_nv`** | `123456` | `NV_HN_02` | Nguyễn Thị Hoa | **Nhân viên** | Phòng Nhân Sự | **HN** | **Nghiệp vụ nhân sự**: Thêm/Sửa nhân viên phòng ban khác (trừ đồng nghiệp phòng NS). Lương bị giấu hoàn toàn. |
| **`taivu_truong`** | `123456` | `NV_HN_04` | Trần Văn Bình | **Trưởng phòng** | Phòng Tài Vụ | **HN** | **Quản lý quỹ lương toàn tập đoàn**: Xem toàn bộ lương 3 miền. Thông tin cá nhân (PII) của nhân viên phòng khác bị che giấu (`*** Bảo mật ***`). |
| **`taivu_nv`** | `123456` | `NV_HN_05` | Lê Thị Chi | **Nhân viên** | Phòng Tài Vụ | **HN** | **Đối soát chi trả lương**: Xem toàn bộ số liệu lương nhân viên 3 miền; PII nhân viên ngoài phòng Tài vụ bị Masking. |
| **`kinhdoanh_tp`** | `123456` | `NV_HCM_02` | Hoàng Văn Dũng | **Trưởng phòng** | Phòng Kinh Doanh | **HCM** | **Cục bộ phòng ban**: Xem danh sách và đầy đủ lương của nhân viên thuộc phòng mình tại chi nhánh HCM (Read-only). |
| **`kinhdoanh_nv`** | `123456` | `NV_HCM_03` | Phan Thị Én | **Nhân viên** | Phòng Kinh Doanh | **HCM** | **Cá nhân & Nội bộ**: Xem hồ sơ, phiếu lương của chính mình, dự án tham gia, chấm công. Lương đồng nghiệp cùng phòng bị Masking (`***`). |

---

## 5. Các Kịch bản Kiểm thử & Tính năng Đặc biệt

1. **Minh chứng Đẩy điều kiện lọc phân tán (Remote Predicate Pushdown):**
   * Truy vấn trên `v_HoSoNhanSu_ToanDien` với điều kiện `WHERE ChiNhanh = 'HCM' AND XepLoai_KPI_Q1 = 'A'`.
   * Chạy `EXPLAIN ANALYZE` để thấy PostgreSQL Coordinator đẩy toàn bộ lệnh lọc xuống Foreign Server `srv_hcm` thay vì kéo toàn bộ bảng về bộ nhớ.
2. **Kịch bản Chịu lỗi Graceful Degradation khi sập 1 Node:**
   * Dừng thử nghiệm container Đà Nẵng: `docker stop site_dn`.
   * Truy cập trang Giám sát Hệ thống (`/monitor/system`): Hệ thống hiển thị đèn đỏ cảnh báo chi nhánh ĐN Offline kèm độ trễ `Timeout`, trong khi các chi nhánh HN và HCM vẫn hoạt động bình thường mà không làm sập ứng dụng.
3. **Thao tác Bù trừ 2 pha (Multi-Model Compensation):**
   * Tải lên ảnh và nhập thông tin nhân viên mới cố tình vi phạm ràng buộc (ví dụ trùng Trưởng phòng).
   * Backend tự động Rollback Transaction SQL và gọi hàm xóa đền bù file rác vừa upload trên MinIO.
