import React, { useState } from 'react';
import { Layout, Menu, Button, Avatar, Dropdown, Typography, Space, Tag } from 'antd';
import {
  DashboardOutlined,
  TeamOutlined,
  DollarOutlined,
  LineChartOutlined,
  AuditOutlined,
  UserOutlined,
  LogoutOutlined,
  ProjectOutlined,
  ApartmentOutlined,
  SolutionOutlined,
  ToolOutlined,
  BarChartOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

export const MainLayout = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const roleId = user?.role_id;
  const position = user?.position || user?.ma_cv || '';
  const deptName = user?.department_name || '';
  const deptId = user?.department_id || '';
  const branch = user?.branch || 'HN';
  const orgType = user?.org_type || user?.loai_don_vi || (deptId.startsWith('PB_HQ_') ? 'TAP_DOAN' : 'CHI_NHANH');

  // Detect Persona based on 4-concept Architecture:
  const isCEO = roleId === 4 || position === 'CEO' || position === 'TGD';
  const isBranchDirector = (roleId === 3 || position === 'GD' || position === 'GD_CN') && !isCEO;
  const isOps = deptName.toLowerCase().includes('vận hành') || deptId.includes('OPS');
  const isHR = deptName.toLowerCase().includes('nhân sự') || deptId.includes('HR');
  const isFinance = deptName.toLowerCase().includes('tài vụ') || deptId.includes('FIN');
  const isDeptManager = roleId === 2 || position === 'TP';

  // Build dynamic menu items strictly adapting to user persona
  const getMenuItems = () => {
    const items = [];

    // Persona 1: CEO (Lãnh đạo Tập đoàn)
    if (isCEO) {
      items.push(
        {
          key: '/dashboard',
          icon: <DashboardOutlined />,
          label: 'Dashboard Toàn quốc',
        },
        {
          key: '/organization/chart',
          icon: <ApartmentOutlined />,
          label: 'Cơ cấu Tập đoàn',
        },
        {
          key: '/employees',
          icon: <TeamOutlined />,
          label: 'Nhân sự Toàn quốc',
        },
        {
          key: '/payroll',
          icon: <DollarOutlined />,
          label: 'Quản trị Lương Toàn quốc',
        },
        {
          key: '/appointments',
          icon: <SolutionOutlined />,
          label: 'Phê duyệt Cấp cao',
        },
        {
          key: '/system-admin/requests',
          icon: <ToolOutlined />,
          label: 'Duyệt Quyền Kỹ thuật',
        },
        {
          key: '/reports',
          icon: <BarChartOutlined />,
          label: 'Báo cáo Chiến lược',
        },
        {
          key: '/system/health',
          icon: <LineChartOutlined />,
          label: 'Giám sát Cụm Phân tán',
        },
        {
          key: '/system/audit',
          icon: <AuditOutlined />,
          label: 'Nhật ký Kiểm toán Toàn cục',
        }
      );
    }
    // Persona 2: Branch Director (Giám đốc Chi nhánh)
    else if (isBranchDirector) {
      items.push(
        {
          key: '/dashboard',
          icon: <DashboardOutlined />,
          label: `Dashboard Chi nhánh (${branch})`,
        },
        {
          key: '/organization/chart',
          icon: <ApartmentOutlined />,
          label: 'Sơ đồ Tổ chức Tập đoàn',
        },
        {
          key: '/employees',
          icon: <TeamOutlined />,
          label: `Nhân sự Chi nhánh (${branch})`,
        },
        {
          key: '/payroll',
          icon: <DollarOutlined />,
          label: `Bảng lương Chi nhánh (${branch})`,
        },
        {
          key: '/appointments',
          icon: <SolutionOutlined />,
          label: `Phê duyệt Chi nhánh (${branch})`,
        },
        {
          key: '/system-admin/requests',
          icon: <ToolOutlined />,
          label: 'Duyệt Yêu cầu Kỹ thuật',
        },
        {
          key: '/reports',
          icon: <BarChartOutlined />,
          label: `Báo cáo Chi nhánh (${branch})`,
        },
        {
          key: '/system/health',
          icon: <LineChartOutlined />,
          label: 'Giám sát Shard Chi nhánh',
        }
      );
    }
    // Persona 3: System Operator (Phòng Vận hành - IT/Ops)
    // Tách biệt quản trị kỹ thuật: Không thấy menu hồ sơ nhân sự / lương!
    else if (isOps) {
      items.push(
        {
          key: '/system/health',
          icon: <LineChartOutlined />,
          label: 'Giám sát Cụm CSDL & MinIO',
        },
        {
          key: '/system-admin/requests',
          icon: <ToolOutlined />,
          label: 'Yêu cầu Bảo trì / Cấp quyền',
        },
        {
          key: '/system/audit',
          icon: <AuditOutlined />,
          label: 'Nhật ký Hoạt động Kỹ thuật',
        },
        {
          key: '/organization/chart',
          icon: <ApartmentOutlined />,
          label: 'Sơ đồ Tổ chức',
        },
        {
          key: '/profile',
          icon: <UserOutlined />,
          label: 'Hồ sơ Cá nhân (ESS)',
        }
      );
    }
    // Persona 4: HR Specialist / HR Manager (Phòng Nhân sự)
    else if (isHR) {
      items.push(
        {
          key: '/employees',
          icon: <TeamOutlined />,
          label: 'Quản trị Nhân sự',
        },
        {
          key: '/appointments',
          icon: <SolutionOutlined />,
          label: 'Bổ nhiệm & Điều chuyển',
        },
        {
          key: '/organization/chart',
          icon: <ApartmentOutlined />,
          label: 'Cơ cấu Tổ chức',
        },
        {
          key: '/projects',
          icon: <ProjectOutlined />,
          label: 'Danh mục Dự án',
        },
        {
          key: '/reports',
          icon: <BarChartOutlined />,
          label: 'Báo cáo Nhân sự',
        },
        {
          key: '/profile',
          icon: <UserOutlined />,
          label: 'Hồ sơ & Phiếu lương của tôi',
        }
      );
    }
    // Persona 5: Finance Specialist / Finance Manager (Phòng Tài vụ)
    else if (isFinance) {
      items.push(
        {
          key: '/payroll',
          icon: <DollarOutlined />,
          label: 'Quyết toán Bảng lương',
        },
        {
          key: '/employees',
          icon: <TeamOutlined />,
          label: 'Danh sách Nhân sự (PII Masked)',
        },
        {
          key: '/organization/chart',
          icon: <ApartmentOutlined />,
          label: 'Cơ cấu Đơn vị',
        },
        {
          key: '/reports',
          icon: <BarChartOutlined />,
          label: 'Báo cáo Quỹ lương',
        },
        {
          key: '/profile',
          icon: <UserOutlined />,
          label: 'Hồ sơ & Phiếu lương của tôi',
        }
      );
    }
    // Persona 6: Department Manager (Trưởng phòng chuyên môn khác)
    else if (isDeptManager) {
      items.push(
        {
          key: '/employees',
          icon: <TeamOutlined />,
          label: 'Nhân sự Phòng ban',
        },
        {
          key: '/organization/chart',
          icon: <ApartmentOutlined />,
          label: 'Sơ đồ Tổ chức',
        },
        {
          key: '/reports',
          icon: <BarChartOutlined />,
          label: 'Báo cáo Phòng ban',
        },
        {
          key: '/profile',
          icon: <UserOutlined />,
          label: 'Hồ sơ & Phiếu lương của tôi',
        }
      );
    }
    // Persona 7: Normal Employee (Nhân viên thông thường)
    else {
      items.push(
        {
          key: '/profile',
          icon: <UserOutlined />,
          label: 'Hồ sơ & Phiếu lương của tôi',
        },
        {
          key: '/employees',
          icon: <TeamOutlined />,
          label: 'Danh bạ Đồng nghiệp',
        },
        {
          key: '/organization/chart',
          icon: <ApartmentOutlined />,
          label: 'Sơ đồ Tổ chức',
        }
      );
    }

    return items;
  };

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'user-info',
      disabled: true,
      label: (
        <div className="py-1">
          <div className="font-semibold text-slate-800">{user?.full_name}</div>
          <div className="text-xs text-slate-400 font-mono">
            {user?.username} ({user?.role_name || user?.position || 'Nhân viên'})
          </div>
          <div className="text-xs text-blue-600">
            {user?.department_name} • {branch} ({orgType === 'TAP_DOAN' ? 'Tập đoàn' : 'Chi nhánh'})
          </div>
        </div>
      ),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      danger: true,
      icon: <LogoutOutlined />,
      label: 'Đăng xuất',
      onClick: handleLogout,
    },
  ];

  return (
    <Layout className="min-h-screen">
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        theme="light"
        width={260}
        className="border-r border-slate-200 shadow-sm"
      >
        <div className="h-16 flex items-center px-4 border-b border-slate-100 gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold tracking-wider">
            X
          </div>
          {!collapsed && (
            <div className="flex flex-col overflow-hidden">
              <span className="font-bold text-slate-800 tracking-tight text-sm truncate">
                SpaceX HRM
              </span>
              <span className="text-[10px] text-slate-400 font-mono tracking-wider">
                ENTERPRISE RESTRUCTURE
              </span>
            </div>
          )}
        </div>

        <div className="py-2">
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={getMenuItems()}
            onClick={handleMenuClick}
            className="border-none font-medium text-slate-700"
          />
        </div>
      </Sider>

      <Layout>
        <Header className="bg-white border-b border-slate-200 px-6 flex items-center justify-between h-16 shadow-xs">
          <div className="flex items-center gap-4">
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              className="text-slate-600 hover:text-slate-900"
            />
            <div className="hidden sm:flex items-center gap-2">
              <span className="text-xs font-medium text-slate-500">Cơ cấu:</span>
              <Tag color={orgType === 'TAP_DOAN' ? 'gold' : 'blue'} className="font-semibold">
                {orgType === 'TAP_DOAN' ? 'TẬP ĐOÀN (HỘI SỞ)' : `CHI NHÁNH ${branch}`}
              </Tag>
              <span className="text-xs font-medium text-slate-500 ml-2">Phòng:</span>
              <span className="text-xs font-semibold text-slate-700">{deptName || 'Hội sở'}</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight" arrow>
              <div className="flex items-center gap-3 cursor-pointer p-1.5 rounded-lg hover:bg-slate-50 transition">
                <Avatar
                  className="bg-blue-600 text-white font-bold"
                  size="default"
                >
                  {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                </Avatar>
                <div className="hidden md:flex flex-col text-left">
                  <span className="text-xs font-semibold text-slate-800 leading-tight">
                    {user?.full_name || 'Người dùng'}
                  </span>
                  <span className="text-[11px] text-slate-400">
                    {user?.role_name || user?.position || 'Nhân viên'}
                  </span>
                </div>
              </div>
            </Dropdown>
          </div>
        </Header>

        <Content className="p-6 bg-slate-50 min-h-[calc(100vh-64px)] overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
