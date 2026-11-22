import React from 'react';
import { Table, Tag, Avatar, Space, Button, Tooltip, Popconfirm } from 'antd';
import { EditOutlined, DeleteOutlined, EyeOutlined, LockOutlined, UserOutlined } from '@ant-design/icons';

/**
 * EmployeeTable: Ant Design table with RBAC-sensitive masking and column control
 */
export const EmployeeTable = ({
  employees = [],
  loading = false,
  pagination = {},
  onTableChange,
  onView,
  onEdit,
  onDelete,
  currentUser,
}) => {
  // Determine role permissions
  const roleId = currentUser?.role_id;
  const isHR =
    currentUser?.department_name?.toLowerCase().includes('nhân sự') ||
    currentUser?.department_id === 'PB_HN_02' ||
    roleId === 4; // General Director can do read operations

  const canEdit =
    currentUser?.department_name?.toLowerCase().includes('nhân sự') ||
    roleId === 2 ||
    roleId === 4;

  const columns = [
    {
      title: 'Nhân viên',
      key: 'employee',
      width: 240,
      render: (_, record) => {
        const isMasked = record.ho_ten === '*** Bảo mật ***';
        return (
          <div className="flex items-center gap-3">
            <Avatar
              src={record.url_avatar}
              icon={<UserOutlined />}
              size={42}
              className="flex-shrink-0 bg-blue-100 text-blue-600 border border-slate-200"
            />
            <div className="min-w-0">
              <div className="font-semibold text-slate-900 truncate">
                {record.ho_ten || 'Chưa cập nhật'}
              </div>
              <div className="text-xs text-slate-400 font-mono">
                {record.ma_nv} • {record.phai || 'N/A'}
              </div>
            </div>
          </div>
        );
      },
    },
    {
      title: 'Chi nhánh & Phòng ban',
      key: 'org',
      width: 220,
      render: (_, record) => {
        const branchColors = { HN: 'blue', DN: 'green', HCM: 'purple' };
        return (
          <div>
            <div className="flex items-center gap-1.5 mb-1">
              <Tag color={branchColors[record.chi_nhanh] || 'default'} className="font-semibold">
                {record.chi_nhanh}
              </Tag>
              <span className="text-xs font-medium text-slate-700">
                {record.ten_phong_ban || record.ma_pb}
              </span>
            </div>
            <div className="text-xs text-slate-500">
              {record.chuc_vu || 'Nhân viên'}
            </div>
          </div>
        );
      },
    },
    {
      title: 'Liên hệ',
      key: 'contact',
      width: 200,
      render: (_, record) => (
        <div className="text-xs">
          <div className="text-slate-700 truncate">{record.email || '—'}</div>
          <div className="text-slate-400">{record.so_dien_thoai || '—'}</div>
        </div>
      ),
    },
    {
      title: 'KPI Q1',
      dataIndex: 'kpi_q1',
      key: 'kpi_q1',
      width: 90,
      align: 'center',
      render: (grade) => {
        if (!grade) return <span className="text-slate-300">—</span>;
        const color = grade === 'A' ? 'gold' : grade === 'B' ? 'blue' : 'default';
        return <Tag color={color} className="font-bold">{grade}</Tag>;
      },
    },
    {
      title: 'Lương thực lĩnh',
      key: 'salary',
      width: 160,
      align: 'right',
      render: (_, record) => {
        if (record.is_salary_masked || record.luong_thuc_linh === null || record.luong_thuc_linh === undefined) {
          return (
            <Tooltip title="Dữ liệu lương được bảo mật theo quy định RBAC">
              <span className="inline-flex items-center gap-1 text-xs text-slate-400 italic bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
                <LockOutlined className="text-slate-400" /> Bảo mật
              </span>
            </Tooltip>
          );
        }
        return (
          <span className="font-semibold text-emerald-600 font-mono">
            {Number(record.luong_thuc_linh).toLocaleString('vi-VN')} đ
          </span>
        );
      },
    },
    {
      title: 'Thao tác',
      key: 'actions',
      width: 140,
      align: 'center',
      render: (_, record) => (
        <Space size="small">
          {onView && (
            <Tooltip title="Xem chi tiết hồ sơ">
              <Button
                type="text"
                size="small"
                icon={<EyeOutlined />}
                onClick={() => onView(record)}
              />
            </Tooltip>
          )}
          {canEdit && onEdit && (
            <Tooltip title="Chỉnh sửa hồ sơ">
              <Button
                type="text"
                size="small"
                className="text-blue-600 hover:text-blue-800"
                icon={<EditOutlined />}
                onClick={() => onEdit(record)}
              />
            </Tooltip>
          )}
          {canEdit && onDelete && (
            <Popconfirm
              title="Xóa nhân viên"
              description={`Bạn có chắc muốn xóa nhân sự ${record.ho_ten}?`}
              onConfirm={() => onDelete(record.ma_nv)}
              okText="Đồng ý"
              cancelText="Hủy"
              okButtonProps={{ danger: true }}
            >
              <Tooltip title="Xóa nhân sự">
                <Button
                  type="text"
                  size="small"
                  danger
                  icon={<DeleteOutlined />}
                />
              </Tooltip>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={employees}
      rowKey={(record) => record.ma_nv}
      loading={loading}
      pagination={{
        current: pagination.current || 1,
        pageSize: pagination.pageSize || 10,
        total: pagination.total || 0,
        showSizeChanger: true,
        pageSizeOptions: ['10', '20', '50'],
        showTotal: (total) => `Tổng cộng ${total} nhân sự`,
      }}
      onChange={onTableChange}
      className="border border-slate-200 rounded-lg overflow-hidden bg-white shadow-sm"
      size="middle"
    />
  );
};

export default EmployeeTable;
