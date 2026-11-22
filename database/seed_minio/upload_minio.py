import os
import json
from minio import Minio
from minio.error import S3Error

# 1. THÔNG SỐ CẤU HÌNH MINIO (Khớp với docker-compose.yml)
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "admin_minio"
MINIO_SECRET_KEY = "PasswordMinio_123"
BUCKET_NAME = "nhansu-bucket"
LOCAL_IMAGE_DIR = "images"

def setup_and_upload():
    try:
        # Khởi tạo MinIO Client
        print(f"[*] Đang kết nối tới MinIO Server tại {MINIO_ENDPOINT}...")
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False  # Đặt False vì đang chạy HTTP trên máy local/Docker
        )
        print("[+] Kết nối thành công!")

        # 2. KIỂM TRA VÀ TẠO BUCKET
        if not client.bucket_exists(BUCKET_NAME):
            print(f"[*] Bucket '{BUCKET_NAME}' chưa tồn tại. Đang tiến hành tạo mới...")
            client.make_bucket(BUCKET_NAME)
            print(f"[+] Tạo bucket '{BUCKET_NAME}' thành công!")
        else:
            print(f"[+] Bucket '{BUCKET_NAME}' đã tồn tại.")

        # 3. THIẾT LẬP ACCESS POLICY CHO PHÉP TRUY CẬP ẢNH CÔNG KHAI (READ-ONLY)
        # Giúp View v_HoSoNhanSu_ToanDien mở được link ảnh trực tiếp trên trình duyệt
        public_read_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                    "Resource": [f"arn:aws:s3:::{BUCKET_NAME}"]
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{BUCKET_NAME}/*"]
                }
            ]
        }
        client.set_bucket_policy(BUCKET_NAME, json.dumps(public_read_policy))
        print(f"[+] Đã cấu hình Public Access Policy cho bucket '{BUCKET_NAME}'.")

        # 4. CHUẨN BỊ THƯ MỤC ẢNH VÀ UPLOAD
        if not os.path.exists(LOCAL_IMAGE_DIR):
            os.makedirs(LOCAL_IMAGE_DIR)
            print(f"[*] Thư mục '{LOCAL_IMAGE_DIR}' vừa được tạo tự động.")

        # Danh sách các tệp mẫu cần đồng bộ cho 3 site
        sample_avatars = ["NV_HN_01.jpg", "NV_HN_02.jpg", "NV_DN_01.jpg", "NV_HCM_01.jpg"]
        
        # Tạo file ảnh giả lập nếu chưa có sẵn trong máy
        for img_name in sample_avatars:
            file_path = os.path.join(LOCAL_IMAGE_DIR, img_name)
            if not os.path.exists(file_path):
                with open(file_path, "wb") as f:
                    f.write(b"SAMPLE_IMAGE_DATA_FOR_DEMO")
                print(f"[*] Đã tạo file ảnh mẫu: {file_path}")

        print("\n[*] Bắt đầu tải ảnh đại diện lên MinIO...")
        for filename in os.listdir(LOCAL_IMAGE_DIR):
            local_file_path = os.path.join(LOCAL_IMAGE_DIR, filename)
            
            if os.path.isfile(local_file_path):
                # Đường dẫn đích trên MinIO (object_name) phải khớp với avatar_key trong CSDL
                object_name = f"avatars/{filename}"
                
                # Tải file lên bucket
                client.fput_object(
                    bucket_name=BUCKET_NAME,
                    object_name=object_name,
                    file_path=local_file_path,
                    content_type="image/jpeg"
                )
                
                # URL truy cập trực tiếp
                public_url = f"http://{MINIO_ENDPOINT}/{BUCKET_NAME}/{object_name}"
                print(f" -> Tải thành công '{filename}' -> Object Key: '{object_name}'")
                print(f"    URL: {public_url}")

        print("\n[V] Hoàn tất toàn bộ quy trình đồng bộ dữ liệu phi cấu trúc!")

    except S3Error as s3_err:
        print(f"[-] Lỗi MinIO S3: {s3_err}")
    except Exception as e:
        print(f"[-] Đã xảy ra lỗi: {e}")

if __name__ == "__main__":
    setup_and_upload()