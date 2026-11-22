import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  InputNumber,
  Row,
  Col,
  Select,
  Tag,
  Typography,
  message,
  Space,
} from 'antd';
import { DollarOutlined, EditOutlined, ReloadOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';
import payrollApi from '../../api/payrollApi';

const { Title, Text } = Typography;
const { Option } = Select;

export const PayrollManager = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [payrollList, setPayrollList] = useState([]);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [updating, setUpdating] = useState(false);

  // Filters
  const [month, setMonth] = useState(3);
  const [year, setYear] = useState(2026);
  const [branchFilter, setBranchFilter] = useState('');

  const [form] = Form.useForm();

  const isGeneralDirector = user?.role_id === 4;
  const isBranchDirector = user?.role_id === 3;
  const canUpdateSalary = isGeneralDirector || isBranchDirector;

  const fetchPayroll = async () => {
    setLoading(true);
    try {
      const params = { month, year };
      if (branchFilter) params.branch = branchFilter;
      const res = await payrollApi.getPayroll(params);
      if (res && res.data) {
        setPayrollList(Array.isArray(res.data) ? res.data : res.data.items || []);
      }
    } catch (err) {
      console.error('Fetch payroll error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPayroll();
  }, [month, year, branchFilter]);

  const handleOpenEdit = (record) => {
    setSelectedRecord(record);
    form.setFieldsValue({
      luong_co_ban: Number(record.luong_co_ban) || 0,
      phu_cap: Number(record.phu_cap) || 0,
      thuong: Number(record.thuong) || 0,
      khau_tru: Number(record.khau_tru) || 0,
    });
    setIsModalOpen(true);
  };

  const handleUpdateSubmit = async () => {
    try {
      const values = await form.validateFields();
      setUpdating(true);

      const payload = {
        thang: month,
        nam: year,
        luong_co_ban: values.luong_co_ban,
        phu_cap: values.phu_cap,
        thuong: values.thuong,
        khau_tru: values.khau_tru,
      };

      await payrollApi.updatePayroll(selectedRecord.ma_nv, payload);
      message.success(`Đã cập nhật lương cho nhân viên ${selectedRecord.ma_nv} thành công!`);
      setIsModalOpen(false);
      fetchPayroll();
    } catch (err) {
      console.error('Update payroll error:', err);
    } finally {
      setUpdating(false);
    }
  };

  const columns = [
    {
      title: 'Nhân viên',
      key: 'employee',
      width: 220,
      render: (_, record) => (
        <div>
          <div className="font-semibold text-slate-800">{record.ho_ten || '***'}</div>
          <div className="text-xs font-mono text-slate-400">
            {record.ma_nv} • <Tag color="blue">{record.chi_nhanh || record.ma_cn}</Tag>
          </div>
        </div>
      ),
    },
    {
      title: 'Phòng ban',
      key: 'dept',
      width: 180,
      render: (_, record) => (
        <span className="text-xs text-slate-600">{record.ten_phong_ban || record.ma_pb}</span>
      ),
    },
    {
      title: 'Lương cơ bản',
      dataIndex: 'luong_co_ban',
      key: 'luong_co_ban',
      align: 'right',
      render: (val) => (
        <span className="font-mono text-slate-700">
          {val !== null && val !== undefined ? Number(val).toLocaleString('vi-VN') + ' đ' : '***'}
        </span>
      ),
    },
    {
      title: 'Phụ cấp',
      dataIndex: 'phu_cap',
      key: 'phu_cap',
      align: 'right',
      render: (val) => (
        <span className="font-mono text-slate-600">
          {val !== null && val !== undefined ? Number(val).toLocaleString('vi-VN') + ' đ' : '***'}
        </span>
      ),
    },
    {
      title: 'Thưởng',
      dataIndex: 'thuong',
      key: 'thuong',
      align: 'right',
      render: (val) => (
        <span className="font-mono text-emerald-600 font-medium">
          {val !== null && val !== undefined ? Number(val).toLocaleString('vi-VN') + ' đ' : '***'}
        </span>
      ),
    },
    {
      title: 'Khấu trừ',
      dataIndex: 'khau_tru',
      key: 'khau_tru',
      align: 'right',
      render: (val) => (
        <span className="font-mono text-rose-500">
          {val !== null && val !== undefined ? Number(val).toLocaleString('vi-VN') + ' đ' : '***'}
        </span>
      ),
    },
    {
      title: 'Lương thực lĩnh',
      key: 'luong_thuc_linh',
      align: 'right',
      render: (_, record) => {
        const val = record.luong_thuc_linh;
        return (
          <span className="font-mono font-bold text-blue-700 text-sm">
            {val !== null && val !== undefined ? Number(val).toLocaleString('vi-VN') + ' đ' : '***'}
          </span>
        );
      },
    },
    {
      title: 'Thao tác',
      key: 'action',
      width: 120,
      align: 'center',
      render: (_, record) => {
        // Validation: Branch Director can only edit their own branch
        const canEditThis =
          isGeneralDirector ||
          (isBranchDirector && (record.chi_nhanh === user?.branch || record.ma_cn === user?.branch));

        if (!canEditThis) {
          return <span className="text-xs text-slate-300 italic">Chỉ đọc</span>;
        }

        return (
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleOpenEdit(record)}
          >
            Điều chỉnh
          </Button>
        );
      },
    },
  ];

  return (
    <div className="space-y-4">
      {/* Top Filter Header */}
      <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <Title level={4} className="!mb-0 text-slate-800">
              Quản trị Lương & Quyết toán Quỹ lương
            </Title>
            <Text className="text-slate-500 text-xs">
              Công thức: Lương thực lĩnh = Lương cơ bản + Phụ cấp + Thưởng - Khấu trừ
            </Text>
          </div>

          <div className="flex items-center gap-3">
            <Select value={month} onChange={(val) => setMonth(val)} style={{ width: 110 }}>
              {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                <Option key={m} value={m}>
                  Tháng {m}
                </Option>
              ))}
            </Select>

            <Select value={year} onChange={(val) => setYear(val)} style={{ width: 100 }}>
              <Option value={2026}>2026</Option>
              <Option value={2025}>2025</Option>
            </Select>

            {isGeneralDirector && (
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

            <Button icon={<ReloadOutlined />} onClick={fetchPayroll}>
              Làm mới
            </Button>
          </div>
        </div>
      </Card>

      {/* Main Table */}
      <Table
        columns={columns}
        dataSource={payrollList}
        rowKey={(record) => record.ma_luong || record.ma_nv}
        loading={loading}
        pagination={{ pageSize: 15 }}
        className="border border-slate-200 rounded-lg overflow-hidden bg-white shadow-sm"
        size="middle"
      />

      {/* Salary Adjustment Modal */}
      <Modal
        title={
          <div className="flex items-center gap-2">
            <DollarOutlined className="text-emerald-600" />
            <span>Điều chỉnh Lương: {selectedRecord?.ho_ten} ({selectedRecord?.ma_nv})</span>
          </div>
        }
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={[
          <Button key="cancel" onClick={() => setIsModalOpen(false)}>
            Hủy
          </Button>,
          <Button
            key="submit"
            type="primary"
            onClick={handleUpdateSubmit}
            loading={updating}
            className="bg-blue-600"
          >
            Lưu & Tính lương tự động
          </Button>,
        ]}
      >
        <Form form={form} layout="vertical" className="mt-4">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="luong_co_ban"
                label="Lương cơ bản (VNĐ)"
                rules={[{ required: true, message: 'Nhập lương cơ bản >= 0' }]}
              >
                <InputNumber
                  className="w-full"
                  formatter={(val) => `${val}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={(val) => val.replace(/\$\s?|(,*)/g, '')}
                  min={0}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="phu_cap" label="Phụ cấp (VNĐ)">
                <InputNumber
                  className="w-full"
                  formatter={(val) => `${val}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={(val) => val.replace(/\$\s?|(,*)/g, '')}
                  min={0}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="thuong" label="Thưởng hiệu suất KPI (VNĐ)">
                <InputNumber
                  className="w-full"
                  formatter={(val) => `${val}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={(val) => val.replace(/\$\s?|(,*)/g, '')}
                  min={0}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="khau_tru" label="Khấu trừ bảo hiểm/thuế (VNĐ)">
                <InputNumber
                  className="w-full"
                  formatter={(val) => `${val}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={(val) => val.replace(/\$\s?|(,*)/g, '')}
                  min={0}
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default PayrollManager;
