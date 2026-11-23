import React from 'react';
import { Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const Forbidden403 = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleBackHome = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <Result
        status="403"
        title="403 - Quyền truy cập bị từ chối"
        subTitle="Bạn không có đủ thẩm quyền truy cập tài nguyên này theo ma trận phân quyền (RBAC) của SpaceX HRM."
        extra={
          <Button type="primary" onClick={handleBackHome} className="bg-blue-600">
            Quay lại trang chính của bạn
          </Button>
        }
      />
    </div>
  );
};

export default Forbidden403;
