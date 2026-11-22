import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import MainLayout from '../layouts/MainLayout';

// Auth Pages
import LoginPage from '../pages/auth/LoginPage';
import Forbidden403 from '../pages/auth/Forbidden403';

// Features Pages
import GlobalDashboard from '../pages/director/GlobalDashboard';
import EmployeeList from '../pages/hr/EmployeeList';
import PayrollManager from '../pages/finance/PayrollManager';
import MyProfile from '../pages/employee/MyProfile';
import SystemHealth from '../pages/monitor/SystemHealth';
import ProjectsPage from '../pages/projects/ProjectsPage';

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/403" element={<Forbidden403 />} />

      {/* Protected routes wrapped in MainLayout */}
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

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute allowedRoles={[3, 4]}>
            <MainLayout>
              <GlobalDashboard />
            </MainLayout>
          </ProtectedRoute>
        }
      />

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

      <Route
        path="/payroll"
        element={
          <ProtectedRoute allowedRoles={[3, 4]} allowedDepartments={['tài vụ']}>
            <MainLayout>
              <PayrollManager />
            </MainLayout>
          </ProtectedRoute>
        }
      />

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

      <Route
        path="/projects"
        element={
          <ProtectedRoute>
            <MainLayout>
              <ProjectsPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/system/health"
        element={
          <ProtectedRoute allowedRoles={[3, 4]}>
            <MainLayout>
              <SystemHealth />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/system/audit"
        element={
          <ProtectedRoute allowedRoles={[2, 3, 4]}>
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
