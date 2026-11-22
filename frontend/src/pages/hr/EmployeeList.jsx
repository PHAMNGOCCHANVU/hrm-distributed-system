import React, { useState, useEffect } from 'react';
import {
  Card,
  Input,
  Select,
  Button,
  Space,
  Row,
  Col,
  Modal,
  Descriptions,
  Tag,
  Avatar,
  message,
} from 'antd';
import {
  SearchOutlined,
  PlusOutlined,
  FilterOutlined,
  ReloadOutlined,
  UserOutlined,
  FilePdfOutlined,
} from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';
import employeeApi from '../../api/employeeApi';
import EmployeeTable from '../../components/EmployeeTable';
import EmployeeForm from './EmployeeForm';

const { Option } = Select;

export const EmployeeList = () => {
  const { user } = useAuth();
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });

  // Filters
  const [searchText, setSearchText] = useState('');
  const [branchFilter, setBranchFilter] = useState('');
  const [kpiFilter, setKpiFilter] = useState('');

  // Modals & Drawers
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [viewDetailModal, setViewDetailModal] = useState(false);
  const [detailData, setDetailData] = useState(null);

  const isGeneralDirector = user?.role_id === 4;
  const isBranchDirector = user?.role_id === 3;
  const isHR =
    user?.department_name?.toLowerCase().includes('nhân sự') ||
    user?.department_id === 'PB_HN_02' ||
    user?.role_id === 2;

  const fetchEmployees = async (page = 1, pageSize = 10) => {
    setLoading(true);
    try {
      const params = {
        page,
        page_size: pageSize,
      };
      if (searchText) params.search = searchText;
      if (branchFilter) params.branch = branchFilter;
      if (kpiFilter) params.kpi_grade = kpiFilter;

      const res = await employeeApi.getAll(params);
      if (res && res.data) {
        setEmployees(res.data.items || []);
        setPagination({
          current: res.data.page || 1,
          pageSize: res.data.page_size || 10,
          total: res.data.total || 0,
        });
      }
    } catch (err) {
      console.error('Fetch employees error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees(1, pagination.pageSize);
  }, [branchFilter, kpiFilter]);

  const handleSearch = () => {
    fetchEmployees(1, pagination.pageSize);
  };

  const handleTableChange = (newPagination) => {
    fetchEmployees(newPagination.current, newPagination.pageSize);
  };

  const handleView = async (record) => {
    try {
      const res = await employeeApi.getById(record.ma_nv);
      if (res && res.data) {
        setDetailData(res.data);
      } else {
        setDetailData(record);
      }
      setViewDetailModal(true);
    } catch (err) {
      setDetailData(record);
      setViewDetailModal(true);
    }
  };

  const handleEdit = (record) => {
    setSelectedEmployee(record);
    setIsFormOpen(true);
  };

  const handleDelete = async (maNv) => {
    try {
      await employeeApi.delete(maNv);
      message.success(`Đã xóa thành công nhân viên ${maNv}`);
      fetchEmployees(pagination.current, pagination.pageSize);
    } catch (err) {
      console.error('Delete employee error:', err);
    }
  };

  const handleFormSuccess = () => {
    setIsFormOpen(false);
    setSelectedEmployee(null);
    fetchEmployees(pagination.current, pagination.pageSize);
  };

  return (
    <div className="space-y-4">
      {/* Search and Action Bar */}
      <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
        <Row gutter={[16, 16]} justify="space-between" align="middle">
          <Col xs={24} md={16} lg={18}>
            <div className="flex flex-wrap items-center gap-3">
              <Input
                placeholder="Tìm theo Tên, Mã NV, Email..."
                prefix={<SearchOutlined className="text-slate-400" />}
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onPressEnter={handleSearch}
                style={{ width: 260 }}
                allowClear
              />

              {/* Branch filter: Enabled for General Director & Finance */}
              {(isGeneralDirector || user?.department_name?.toLowerCase().includes('tài vụ')) && (
                <Select
                  placeholder="Tất cả Chi nhánh"
                  value={branchFilter || undefined}
                  onChange={(val) => setBranchFilter(val || '')}
                  style={{ width: 160 }}
                  allowClear
                >
                  <Option value="HN">Hà Nội (Hội sở)</Option>
                  <Option value="DN">Đà Nẵng</Option>
                  <Option value="HCM">TP.HCM</Option>
                </Select>
              )}

              <Select
                placeholder="Lọc theo KPI"
                value={kpiFilter || undefined}
                onChange={(val) => setKpiFilter(val || '')}
                style={{ width: 150 }}
                allowClear
              >
                <Option value="A">Hạng A (Xuất sắc)</Option>
                <Option value="B">Hạng B (Hoàn thành)</Option>
                <Option value="C">Hạng C (Cần cải thiện)</Option>
              </Select>

              <Button icon={<SearchOutlined />} onClick={handleSearch} type="primary" className="bg-blue-600">
                Tìm kiếm
              </Button>
              <Button icon={<ReloadOutlined />} onClick={() => fetchEmployees(1, pagination.pageSize)}>
                Làm mới
              </Button>
            </div>
          </Col>

          <Col xs={24} md={8} lg={6} className="text-right">
            {isHR && (
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => {
                  setSelectedEmployee(null);
                  setIsFormOpen(true);
                }}
                className="bg-blue-600 font-semibold"
              >
                Thêm nhân sự mới
              </Button>
            )}
          </Col>
        </Row>
      </Card>

      {/* Main Employee Table */}
      <EmployeeTable
        employees={employees}
        loading={loading}
        pagination={pagination}
        onTableChange={handleTableChange}
        onView={handleView}
        onEdit={handleEdit}
        onDelete={handleDelete}
        currentUser={user}
      />

      {/* Form Drawer/Modal */}
      {isFormOpen && (
        <EmployeeForm
          visible={isFormOpen}
          onClose={() => {
            setIsFormOpen(false);
            setSelectedEmployee(null);
          }}
          onSuccess={handleFormSuccess}
          initialData={selectedEmployee}
          currentUser={user}
        />
      )}

      {/* View Detail Modal */}
      <Modal
        title={
          <div className="flex items-center gap-2">
            <Avatar src={detailData?.url_avatar} icon={<UserOutlined />} size="small" />
            <span className="font-bold text-slate-800">
              Chi tiết Hồ sơ Nhân sự: {detailData?.ho_ten}
            </span>
          </div>
        }
        open={viewDetailModal}
        onCancel={() => setViewDetailModal(false)}
        footer={[
          <Button key="close" onClick={() => setViewDetailModal(false)}>
            Đóng
          </Button>,
        ]}
        width={750}
      >
        {detailData && (
          <div className="py-2 space-y-4">
            <Descriptions bordered size="small" column={2}>
              <Descriptions.Item label="Mã nhân viên" span={1}>
                <span className="font-mono font-semibold">{detailData.ma_nv}</span>
              </Descriptions.Item>
              <Descriptions.Item label="Chi nhánh" span={1}>
                <Tag color="blue">{detailData.chi_nhanh || detailData.ma_cn}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Họ và tên" span={1}>
                {detailData.ho_ten}
              </Descriptions.Item>
              <Descriptions.Item label="Giới tính" span={1}>
                {detailData.phai || '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Phòng ban" span={1}>
                {detailData.ten_phong_ban || detailData.ma_pb}
              </Descriptions.Item>
              <Descriptions.Item label="Chức vụ" span={1}>
                {detailData.chuc_vu || detailData.ma_cv}
              </Descriptions.Item>
              <Descriptions.Item label="Email" span={1}>
                {detailData.email || '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Số điện thoại" span={1}>
                {detailData.so_dien_thoai || '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Mã số thuế" span={1}>
                {detailData.ma_so_thue || '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Trạng thái" span={1}>
                <Tag color="green">{detailData.trang_thai || 'DangLamViec'}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Bản Scan CV" span={2}>
                {detailData.url_cv ? (
                  <a
                    href={detailData.url_cv}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 text-blue-600 hover:underline font-medium"
                  >
                    <FilePdfOutlined className="text-rose-500" /> Xem tệp PDF CV trên MinIO
                  </a>
                ) : (
                  <span className="text-slate-400">Chưa có tệp</span>
                )}
              </Descriptions.Item>
            </Descriptions>

            {/* Skills & KPI */}
            <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
              <div className="text-xs font-semibold text-slate-700 uppercase mb-2">
                Kỹ năng & Năng lực chuyên môn (JSONB)
              </div>
              <div className="flex flex-wrap gap-2">
                {detailData.skills && Array.isArray(detailData.skills) && detailData.skills.length > 0 ? (
                  detailData.skills.map((s, idx) => (
                    <Tag key={idx} color="geekblue" className="px-2.5 py-1">
                      <strong>{s.name}</strong> ({s.level})
                    </Tag>
                  ))
                ) : (
                  <span className="text-xs text-slate-400">Chưa cập nhật kỹ năng</span>
                )}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default EmployeeList;
