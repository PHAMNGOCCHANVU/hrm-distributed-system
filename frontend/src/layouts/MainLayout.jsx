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
  const deptName = user?.department_name || '';
  const branch = user?.branch || 'HN';

  // Build dynamic menu items according to role
  const getMenuItems = () => {
    const items = [];

    // 1. General Director (Role 4)
    if (roleId === 4) {
      items.push(
        {
          key: '/dashboard',
          icon: <DashboardOutlined />,
          label: 'Dashboard Tập đoàn',
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
          key: '/system/health',
          icon: <LineChartOutlined />,
          label: 'Sức khỏe Cụm Phân tán',
        },
        {
          key: '/system/audit',
          icon: <AuditOutlined />,
          label: 'Nhật ký Kiểm toán Toàn tập đoàn',
        }
      );
    }
    // 2. Branch Director (Role 3)
    else if (roleId === 3) {
      items.push(
        {
          key: '/dashboard',
          icon: <DashboardOutlined />,
          label: `Dashboard Chi nhánh (${branch})`,
        },
        {
          key: '/employees',
          icon: <TeamOutlined />,
          label: `Nhân sự Chi nhánh (${branch})`,
        },
        {
          key: '/payroll',
          icon: <DollarOutlined />,
          label: `Lương Chi nhánh (${branch})`,
        },
        {
          key: '/system/health',
          icon: <LineChartOutlined />,
          label: 'Giám sát Node & CSDL',
        }
      );
    }
    // 3. HR (Staff or Manager)
    else if (deptName.toLowerCase().includes('nhân sự') || user?.department_id === 'PB_HN_02') {
      items.push(
        {
          key: '/employees',
          icon: <TeamOutlined />,
          label: 'Quản trị Nhân sự',
        },
        {
          key: '/projects',
          icon: <ProjectOutlined />,
          label: 'Danh mục Dự án',
        },
        {
          key: '/profile',
          icon: <UserOutlined />,
          label: 'Hồ sơ & Phiếu lương của tôi',
        }
      );
      if (roleId === 2) {
        items.push({
          key: '/system/audit',
          icon: <AuditOutlined />,
          label: 'Nhật ký Hoạt động Nhân sự',
        });
      }
    }
    // 4. Finance / Payroll Department
    else if (deptName.toLowerCase().includes('tài vụ') || user?.department_id === 'PB_HN_03') {
      items.push(
        {
          key: '/payroll',
          icon: <DollarOutlined />,
          label: 'Quyết toán Bảng lương',
        },
        {
          key: '/employees',
          icon: <TeamOutlined />,
          label: 'Danh sách Nhân sự (Masked)',
        },
        {
          key: '/profile',
          icon: <UserOutlined />,
          label: 'Hồ sơ & Phiếu lương của tôi',
        }
      );
    }
    // 5. Normal Employee
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
          <div className="text-xs text-slate-400 font-mono">{user?.username} ({user?.role_name})</div>
          <div className="text-xs text-blue-600">{user?.department_name} - {user?.branch}</div>
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
                DISTRIBUTED CLUSTER
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
            className="border-none"
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
              <span className="text-xs font-medium text-slate-500">Chi nhánh:</span>
              <Tag color="blue" className="font-semibold">{user?.branch || 'HN'}</Tag>
              <span className="text-xs font-medium text-slate-500 ml-2">Phòng:</span>
              <span className="text-xs font-semibold text-slate-700">{user?.department_name || 'Hội sở'}</span>
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
                    {user?.role_name || 'Nhân viên'}
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
