import React from 'react';
import { Upload, Button, Image, Space, Typography } from 'antd';
import { UploadOutlined, FilePdfOutlined, DeleteOutlined } from '@ant-design/icons';

const { Text } = Typography;

export const FileUploader = ({
  avatarFile,
  setAvatarFile,
  avatarPreview,
  setAvatarPreview,
  cvFile,
  setCvFile,
  currentAvatarUrl,
  currentCvUrl,
}) => {
  const handleAvatarChange = (info) => {
    const file = info.file;
    // When using customRequest or beforeUpload returning false
    if (file) {
      setAvatarFile(file);
      const previewUrl = URL.createObjectURL(file);
      setAvatarPreview(previewUrl);
    }
  };

  const handleCvChange = (info) => {
    const file = info.file;
    if (file) {
      setCvFile(file);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 bg-slate-50 border border-slate-200 rounded-lg">
      {/* Upload Avatar */}
      <div className="flex flex-col items-center justify-center p-4 border border-dashed border-slate-300 rounded-lg bg-white">
        <Text strong className="mb-3 text-slate-700">Ảnh đại diện (MinIO S3)</Text>
        <div className="mb-3">
          {avatarPreview ? (
            <Image
              src={avatarPreview}
              alt="Avatar preview"
              className="w-24 h-24 rounded-full object-cover shadow-sm border"
              width={96}
              height={96}
            />
          ) : currentAvatarUrl ? (
            <Image
              src={currentAvatarUrl}
              alt="Current avatar"
              className="w-24 h-24 rounded-full object-cover shadow-sm border"
              width={96}
              height={96}
              fallback="https://via.placeholder.com/96?text=Avatar"
            />
          ) : (
            <div className="w-24 h-24 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 border border-dashed">
              Chưa có ảnh
            </div>
          )}
        </div>
        <Space orientation="horizontal" size="small">
          <Upload
            accept="image/png,image/jpeg,image/jpg"
            showUploadList={false}
            beforeUpload={(file) => {
              setAvatarFile(file);
              setAvatarPreview(URL.createObjectURL(file));
              return false; // Prevent automatic upload
            }}
          >
            <Button icon={<UploadOutlined />} size="small">Chọn ảnh mới</Button>
          </Upload>
          {avatarFile && (
            <Button
              danger
              size="small"
              icon={<DeleteOutlined />}
              onClick={() => {
                setAvatarFile(null);
                setAvatarPreview(null);
              }}
            >
              Hủy
            </Button>
          )}
        </Space>
        <Text type="secondary" className="text-[11px] mt-2">Định dạng JPG, PNG (tối đa 5MB)</Text>
      </div>

      {/* Upload CV PDF */}
      <div className="flex flex-col items-center justify-center p-4 border border-dashed border-slate-300 rounded-lg bg-white">
        <Text strong className="mb-3 text-slate-700">Tệp Scan CV PDF (MinIO S3)</Text>
        <div className="mb-3 flex flex-col items-center">
          <FilePdfOutlined className="text-4xl text-rose-500 mb-2" />
          {cvFile ? (
            <Text className="text-xs font-semibold text-emerald-600 truncate max-w-[200px]">
              Tệp mới: {cvFile.name}
            </Text>
          ) : currentCvUrl ? (
            <a
              href={currentCvUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-blue-600 hover:underline flex items-center gap-1"
            >
              <span>Xem tệp CV hiện tại</span>
            </a>
          ) : (
            <Text type="secondary" className="text-xs">Chưa có bản scan CV</Text>
          )}
        </div>
        <Space orientation="horizontal" size="small">
          <Upload
            accept="application/pdf"
            showUploadList={false}
            beforeUpload={(file) => {
              setCvFile(file);
              return false; // Prevent automatic upload
            }}
          >
            <Button icon={<UploadOutlined />} size="small">Chọn tệp PDF</Button>
          </Upload>
          {cvFile && (
            <Button
              danger
              size="small"
              icon={<DeleteOutlined />}
              onClick={() => setCvFile(null)}
            >
              Hủy
            </Button>
          )}
        </Space>
        <Text type="secondary" className="text-[11px] mt-2">Định dạng PDF (tối đa 10MB)</Text>
      </div>
    </div>
  );
};

export default FileUploader;
