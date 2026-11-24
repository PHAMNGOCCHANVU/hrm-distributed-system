import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import MainLayout from '../layouts/MainLayout';

// Auth Pages
import LoginPage from '../pages/auth/LoginPage';
import Forbidden403 from '../pages/auth/Forbidden403';

// Core Features Pages
import GlobalDashboard from '../pages/director/GlobalDashboard';
import EmployeeList from '../pages/hr/EmployeeList';
import PayrollManager from '../pages/finance/PayrollManager';
import MyProfile from '../pages/employee/MyProfile';
import SystemHealth from '../pages/monitor/SystemHealth';
import ProjectsPage from '../pages/projects/ProjectsPage';

// Enterprise Restructure Pages (4-concept & Persona architecture)
import OrgChartPage from '../pages/organization/OrgChartPage';
import AppointmentPage from '../pages/appointments/AppointmentPage';
import AdminRequestsPage from '../pages/admin/AdminRequestsPage';
import ReportsPage from '../pages/reports/ReportsPage';

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/403" element={<Forbidden403 />} />

      {/* Root redirect */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Navigate to="/dashboard" replace />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* Dashboard: CEO, Branch Directors */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute
            allowedPositions={['CEO', 'GD_CN', 'TGD', 'GD', 3, 4]}
            allowedRoles={['GROUP_EXECUTIVE', 'BRANCH_DIRECTOR']}
          >
            <MainLayout>
              <GlobalDashboard />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* Organization Chart: All authenticated users can view */}
      <Route
        path="/organization/chart"
        element={
          <ProtectedRoute>
            <MainLayout>
              <OrgChartPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* Employees: Accessible to CEO, Branch Director, HR, Finance, Managers, and Employees */}
      <Route
        path="/employees"
        element={
          <ProtectedRoute>
            <MainLayout>
              <EmployeeList />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* Payroll: Finance specialists, CEO, Branch Directors */}
      <Route
        path="/payroll"
        element={
          <ProtectedRoute
            allowedPositions={['CEO', 'GD_CN', 'TGD', 'GD', 3, 4]}
            allowedRoles={['GROUP_EXECUTIVE', 'BRANCH_DIRECTOR', 'FINANCE_SPECIALIST']}
            allowedDepartments={['tài vụ', 'FIN']}
          >
            <MainLayout>
              <PayrollManager />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* Appointments: HR Specialists, CEO, Branch Directors */}
      <Route
        path="/appointments"
        element={
          <ProtectedRoute
            allowedPositions={['CEO', 'GD_CN', 'TGD', 'GD', 3, 4]}
            allowedRoles={['GROUP_EXECUTIVE', 'BRANCH_DIRECTOR', 'HR_SPECIALIST']}
            allowedDepartments={['nhân sự', 'HR']}
          >
            <MainLayout>
              <AppointmentPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* System Admin Requests: System Operators (IT/Ops), CEO, Branch Directors */}
      <Route
        path="/system-admin/requests"
        element={
          <ProtectedRoute
            allowedPositions={['CEO', 'GD_CN', 'TGD', 'GD', 3, 4]}
            allowedRoles={['GROUP_EXECUTIVE', 'BRANCH_DIRECTOR', 'SYSTEM_OPERATOR']}
            allowedDepartments={['vận hành', 'OPS']}
          >
            <MainLayout>
              <AdminRequestsPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* Reports Center: Accessible to all personas (data is scoped automatically by backend) */}
      <Route
        path="/reports"
        element={
          <ProtectedRoute>
            <MainLayout>
              <ReportsPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* ESS Profile: All authenticated employees */}
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <MainLayout>
              <MyProfile />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* Projects: HR specialists, CEO */}
      <Route
        path="/projects"
        element={
          <ProtectedRoute
            allowedPositions={['CEO', 'TGD', 4]}
            allowedRoles={['GROUP_EXECUTIVE', 'HR_SPECIALIST']}
            allowedDepartments={['nhân sự', 'HR']}
          >
            <MainLayout>
              <ProjectsPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* System Cluster Health: System Operator, CEO, Branch Director */}
      <Route
        path="/system/health"
        element={
          <ProtectedRoute
            allowedPositions={['CEO', 'GD_CN', 'TGD', 'GD', 3, 4]}
            allowedRoles={['GROUP_EXECUTIVE', 'BRANCH_DIRECTOR', 'SYSTEM_OPERATOR']}
            allowedDepartments={['vận hành', 'OPS']}
          >
            <MainLayout>
              <SystemHealth />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* System Audit: CEO, Branch Director, System Operator, HR Manager */}
      <Route
        path="/system/audit"
        element={
          <ProtectedRoute
            allowedPositions={['CEO', 'GD_CN', 'TP', 'TGD', 'GD', 2, 3, 4]}
            allowedRoles={['GROUP_EXECUTIVE', 'BRANCH_DIRECTOR', 'SYSTEM_OPERATOR', 'DEPT_MANAGER']}
            allowedDepartments={['vận hành', 'nhân sự', 'OPS', 'HR']}
          >
            <MainLayout>
              <SystemHealth />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
