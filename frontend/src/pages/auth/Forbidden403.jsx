import React from 'react';
import { Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const Forbidden403 = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleBackHome = () => {
    if (user?.role_id === 4 || user?.role_id === 3) {
      navigate('/dashboard');
    } else if (user?.department_name?.toLowerCase().includes('tài vụ')) {
      navigate('/payroll');
    } else if (user?.department_name?.toLowerCase().includes('nhân sự')) {
      navigate('/employees');
    } else {
      navigate('/profile');
    }
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
