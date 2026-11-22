import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute: Kiểm tra trạng thái đăng nhập, roles và departments
 * @param {Array<string|number>} allowedRoles - Danh sách role_id hoặc role_name được phép
 * @param {Array<string>} allowedDepartments - Danh sách department_name hoặc department_id được phép
 */
const ProtectedRoute = ({ children, allowedRoles = [], allowedDepartments = [] }) => {
  const { user, isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <Spin size="large" tip="Đang tải dữ liệu phiên làm việc..." />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Role validation
  if (allowedRoles.length > 0) {
    const hasRole = allowedRoles.some((role) => {
      if (typeof role === 'number') {
        return user.role_id === role;
      }
      return (
        user.role_name === role ||
        (role === 'General Director' && user.role_id === 4) ||
        (role === 'Branch Director' && user.role_id === 3) ||
        (role === 'Manager' && user.role_id === 2) ||
        (role === 'Employee' && user.role_id === 1)
      );
    });

    if (!hasRole) {
      return <Navigate to="/403" replace />;
    }
  }

  // Department validation
  if (allowedDepartments.length > 0) {
    const hasDept = allowedDepartments.some((dept) => {
      const userDept = user.department_name || '';
      return (
        userDept.toLowerCase().includes(dept.toLowerCase()) ||
        user.department_id === dept
      );
    });

    if (!hasDept) {
      return <Navigate to="/403" replace />;
    }
  }

  return children;
};

export default ProtectedRoute;
