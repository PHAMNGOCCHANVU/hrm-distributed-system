import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute: Kiểm tra trạng thái đăng nhập và quyền truy cập
 * Tuân thủ mô hình 4 Khái niệm (Position, System Roles, Scope, Business Authority).
 * Không áp đặt điều kiện AND cứng nhắc giữa Role và Department.
 * Bất cứ khi nào một route được hiển thị trên menu của người dùng, họ có quyền truy cập hợp lệ 100%.
 *
 * @param {Array<string|number>} allowedPositions - Chức vụ cho phép (e.g., 'CEO', 'GD_CN', 'TP', 'NV', 1, 2, 3, 4)
 * @param {Array<string>} allowedRoles - Vai trò hệ thống cho phép (e.g., 'GROUP_EXECUTIVE', 'BRANCH_DIRECTOR', 'DEPT_MANAGER', 'HR_SPECIALIST', 'FINANCE_SPECIALIST', 'SYSTEM_OPERATOR', 'EMPLOYEE')
 * @param {Array<string>} allowedDepartments - Phòng ban cho phép (dạng tên hoặc mã phòng ban)
 * @param {Array<string>} allowedScopes - Phạm vi dữ liệu ('GLOBAL', 'BRANCH', 'DEPARTMENT', 'PERSONAL')
 * @param {Function} customCheck - Hàm kiểm tra tùy chỉnh tùy theo logic nghiệp vụ
 */
const ProtectedRoute = ({
  children,
  allowedPositions = [],
  allowedRoles = [],
  allowedDepartments = [],
  allowedScopes = [],
  customCheck = null,
}) => {
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

  // If no restrictions are specified, any authenticated user can access
  if (
    allowedPositions.length === 0 &&
    allowedRoles.length === 0 &&
    allowedDepartments.length === 0 &&
    allowedScopes.length === 0 &&
    !customCheck
  ) {
    return children;
  }

  // 1. Custom check hook if provided
  if (customCheck && typeof customCheck === 'function') {
    if (customCheck(user)) {
      return children;
    }
  }

  // Extract user parameters
  const userPosition = user.position || user.ma_cv || '';
  const userRoleId = user.role_id;
  const userRoleName = user.role_name || '';
  const userSystemRoles = Array.isArray(user.system_roles)
    ? user.system_roles
    : (user.system_roles ? [user.system_roles] : []);
  const userDept = user.department_name || '';
  const userDeptId = user.department_id || '';
  const userScope = user.scope || user.data_scope || '';

  // Check 1: Position match
  const matchesPosition =
    allowedPositions.length === 0 ||
    allowedPositions.some((pos) => {
      if (typeof pos === 'number') {
        return userRoleId === pos;
      }
      return (
        userPosition.toUpperCase() === pos.toUpperCase() ||
        (pos === 'CEO' && (userRoleId === 4 || userPosition === 'TGD' || userPosition === 'CEO')) ||
        (pos === 'GD_CN' && (userRoleId === 3 || userPosition === 'GD' || userPosition === 'GD_CN')) ||
        (pos === 'TP' && (userRoleId === 2 || userPosition === 'TP')) ||
        (pos === 'NV' && (userRoleId === 1 || userPosition === 'NV'))
      );
    });

  // Check 2: System Role match
  const matchesRole =
    allowedRoles.length === 0 ||
    allowedRoles.some((role) => {
      // Check in system_roles list
      if (userSystemRoles.map(r => r.toUpperCase()).includes(role.toUpperCase())) {
        return true;
      }
      // Check legacy role_name or role_id
      if (role === 'GROUP_EXECUTIVE' && (userRoleId === 4 || userRoleName.includes('Tổng giám đốc'))) return true;
      if (role === 'BRANCH_DIRECTOR' && (userRoleId === 3 || userRoleName.includes('Giám đốc'))) return true;
      if (role === 'DEPT_MANAGER' && (userRoleId === 2 || userRoleName.includes('Trưởng phòng'))) return true;
      if (role === 'HR_SPECIALIST' && (userDept.toLowerCase().includes('nhân sự') || userDeptId.includes('HR'))) return true;
      if (role === 'FINANCE_SPECIALIST' && (userDept.toLowerCase().includes('tài vụ') || userDeptId.includes('FIN'))) return true;
      if (role === 'SYSTEM_OPERATOR' && (userDept.toLowerCase().includes('vận hành') || userDeptId.includes('OPS'))) return true;
      if (role === 'EMPLOYEE' && userRoleId >= 1) return true;

      return userRoleName.toUpperCase() === role.toUpperCase();
    });

  // Check 3: Department match
  const matchesDept =
    allowedDepartments.length === 0 ||
    allowedDepartments.some((dept) => {
      return (
        userDept.toLowerCase().includes(dept.toLowerCase()) ||
        userDeptId.toUpperCase().includes(dept.toUpperCase())
      );
    });

  // Check 4: Scope match
  const matchesScope =
    allowedScopes.length === 0 ||
    allowedScopes.some((sc) => userScope.toUpperCase() === sc.toUpperCase());

  // In our flexible 4-concept model, if ANY of the defined access criteria is met, grant access!
  // This completely eliminates rigid AND condition blocks that lead to 403.
  const hasAccess =
    (allowedPositions.length > 0 && matchesPosition) ||
    (allowedRoles.length > 0 && matchesRole) ||
    (allowedDepartments.length > 0 && matchesDept) ||
    (allowedScopes.length > 0 && matchesScope);

  if (hasAccess) {
    return children;
  }

  // Not authorized
  return <Navigate to="/403" replace />;
};

export default ProtectedRoute;
