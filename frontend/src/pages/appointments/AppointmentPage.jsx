import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  Tag,
  Typography,
  Space,
  Row,
  Col,
  message,
} from 'antd';
import {
  SolutionOutlined,
  PlusOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import appointmentApi from '../../api/appointmentApi';
import catalogApi from '../../api/catalogApi';
import { useAuth } from '../../context/AuthContext';

const { Title, Text } = Typography;
const { Option } = Select;

export const AppointmentPage = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [appointments, setAppointments] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [approveModalOpen, setApproveModalOpen] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const [departments, setDepartments] = useState([]);
  const [form] = Form.useForm();
  const [approveForm] = Form.useForm();

  const isCEO = user?.role_id === 4 || user?.position === 'CEO' || user?.position === 'TGD';
  const isBranchDirector = user?.role_id === 3 || user?.position === 'GD_CN' || user?.position === 'GD';
  const isHR = user?.department_name?.toLowerCase().includes('nhân sự') || user?.department_id?.includes('HR');

  const canPropose = isHR || isCEO;
  const canApprove = isCEO || isBranchDirector;

  const fetchAppointments = async () => {
    setLoading(true);
    try {
      const res = await appointmentApi.getAppointments();
      if (res && res.data) {
        setAppointments(Array.isArray(res.data) ? res.data : res.data.items || []);
      }
    } catch (err) {
      console.error('Fetch appointments error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAppointments();
    catalogApi.getDepartments().then((res) => {
      if (res && res.data) setDepartments(res.data);
    });
  }, []);

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);
      const payload = {
        ma_nv: values.ma_nv,
        chuc_vu_moi: values.chuc_vu_moi,
        ma_pb_moi: values.ma_pb_moi,
        ma_cn_moi: values.ma_cn_moi,
        ly_do: values.ly_do,
        ngay_hieu_luc: values.ngay_hieu_luc ? values.ngay_hieu_luc.format('YYYY-MM-DD') : null,
      };

      await appointmentApi.createAppointment(payload);
      message.success('Tạo phiếu đề xuất bổ nhiệm thành công! Đang chờ Lãnh đạo phê duyệt.');
      setIsModalOpen(false);
      form.resetFields();
      fetchAppointments();
    } catch (err) {
      console.error('Create appointment error:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleApproveSubmit = async (decision) => {
    try {
      const values = await approveForm.validateFields();
      setSubmitting(true);
      await appointmentApi.approveAppointment(selectedAppointment.id || selectedAppointment.ma_quyet_dinh, {
        decision,
        comment: values.comment || (decision === 'APPROVED' ? 'Chấp thuận đề xuất' : 'Từ chối đề xuất'),
      });

      message.success(`Đã xử lý quyết định ${decision === 'APPROVED' ? 'PHÊ DUYỆT' : 'TỪ CHỐI'} thành công!`);
      setApproveModalOpen(false);
      approveForm.resetFields();
      fetchAppointments();
    } catch (err) {
      console.error('Approve error:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    {
      title: 'Mã Phiếu',
      dataIndex: 'ma_quyet_dinh',
      key: 'ma_quyet_dinh',
      render: (val, r) => <span className="font-mono font-semibold">{val || r.id || 'QD_2026_01'}</span>,
    },
    {
      title: 'Nhân sự',
      key: 'employee',
      render: (_, r) => (
        <div>
          <div className="font-semibold text-slate-800">{r.ho_ten || r.ma_nv}</div>
          <div className="text-xs font-mono text-slate-400">{r.ma_nv}</div>
        </div>
      ),
    },
    {
      title: 'Vị trí Bổ nhiệm / Điều chuyển',
      key: 'target',
      render: (_, r) => (
        <div>
          <Tag color="blue">{r.chuc_vu_moi || r.MaCVMoi || 'TP'}</Tag>
          <span className="text-xs text-slate-700">{r.ten_pb_moi || r.ma_pb_moi}</span>
          <div className="text-[11px] text-slate-400 font-mono">Chi nhánh: {r.ma_cn_moi}</div>
        </div>
      ),
    },
    {
      title: 'Lý do / Căn cứ',
      dataIndex: 'ly_do',
      key: 'ly_do',
      render: (val) => <span className="text-xs text-slate-600">{val || '—'}</span>,
    },
    {
      title: 'Trạng thái',
      dataIndex: 'trang_thai',
      key: 'status',
      render: (st) => {
        const s = st || 'PENDING';
        if (s === 'APPROVED') return <Tag color="success">ĐÃ PHÊ DUYỆT</Tag>;
        if (s === 'REJECTED') return <Tag color="error">TỪ CHỐI</Tag>;
        return <Tag color="processing">CHỜ PHÊ DUYỆT</Tag>;
      },
    },
    {
      title: 'Thao tác',
      key: 'actions',
      render: (_, r) => {
        const isPending = (r.trang_thai || 'PENDING') === 'PENDING';
        if (!canApprove || !isPending) {
          return <span className="text-xs text-slate-400 italic">Đã kết thúc</span>;
        }

        return (
          <Button
            type="primary"
            size="small"
            className="bg-blue-600"
            onClick={() => {
              setSelectedAppointment(r);
              setApproveModalOpen(true);
            }}
          >
            Xem xét & Duyệt
          </Button>
        );
      },
    },
  ];

  return (
    <div className="space-y-4">
      <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-50 text-blue-600 rounded-xl text-xl">
              <SolutionOutlined />
            </div>
            <div>
              <Title level={4} className="!mb-0 text-slate-800">
                Quy trình Bổ nhiệm & Điều chuyển Nhân sự (Maker - Checker)
              </Title>
              <Text className="text-slate-500 text-xs">
                Chuyên viên Nhân sự đề xuất $\rightarrow$ Lãnh đạo thẩm quyền (CEO / Giám đốc Chi nhánh) thẩm định & phê duyệt
              </Text>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button icon={<ReloadOutlined />} onClick={fetchAppointments}>
              Làm mới
            </Button>
            {canPropose && (
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setIsModalOpen(true)}
                className="bg-blue-600 font-semibold"
              >
                Tạo Đề Xuất Bổ Nhiệm
              </Button>
            )}
          </div>
        </div>
      </Card>

      <Table
        columns={columns}
        dataSource={appointments}
        rowKey={(r) => r.id || r.ma_quyet_dinh || Math.random()}
        loading={loading}
        className="border border-slate-200 rounded-lg overflow-hidden bg-white shadow-sm"
      />

      {/* Modal Maker: Create Appointment */}
      <Modal
        title="Lập Đề Xuất Bổ Nhiệm / Điều Chuyển (Maker)"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={handleCreate}
        confirmLoading={submitting}
        okText="Gửi đề xuất"
        cancelText="Hủy"
        width={600}
      >
        <Form form={form} layout="vertical" className="mt-4">
          <Form.Item name="ma_nv" label="Mã nhân sự" rules={[{ required: true, message: 'Nhập mã NV' }]}>
            <Input placeholder="VD: NV_DN_01" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="chuc_vu_moi" label="Chức vụ mới" rules={[{ required: true }]}>
                <Select placeholder="Chọn chức vụ">
                  <Option value="TP">Trưởng phòng (TP)</Option>
                  <Option value="GD_CN">Giám đốc Chi nhánh (GD_CN)</Option>
                  <Option value="NV">Nhân viên chuyên trách (NV)</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="ma_cn_moi" label="Chi nhánh mục tiêu" rules={[{ required: true }]}>
                <Select placeholder="Chọn chi nhánh">
                  <Option value="HN">Hà Nội</Option>
                  <Option value="DN">Đà Nẵng</Option>
                  <Option value="HCM">TP.HCM</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="ma_pb_moi" label="Phòng ban mục tiêu" rules={[{ required: true }]}>
            <Select placeholder="Chọn phòng ban">
              {departments.map((d) => (
                <Option key={d.ma_pb} value={d.ma_pb}>
                  {d.ten_pb} ({d.ma_cn})
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="ly_do" label="Lý do / Căn cứ bổ nhiệm" rules={[{ required: true }]}>
            <Input.TextArea rows={3} placeholder="Quy hoạch cán bộ nguồn, đáp ứng năng lực xuất sắc..." />
          </Form.Item>

          <Form.Item name="ngay_hieu_luc" label="Ngày có hiệu lực">
            <DatePicker className="w-full" format="YYYY-MM-DD" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Modal Checker: Approve/Reject */}
      <Modal
        title={`Phê Duyệt Đề Xuất Bổ Nhiệm: ${selectedAppointment?.ho_ten || selectedAppointment?.ma_nv}`}
        open={approveModalOpen}
        onCancel={() => setApproveModalOpen(false)}
        footer={[
          <Button key="reject" danger onClick={() => handleApproveSubmit('REJECTED')} loading={submitting}>
            Từ chối (Reject)
          </Button>,
          <Button
            key="approve"
            type="primary"
            className="bg-emerald-600 hover:bg-emerald-500"
            onClick={() => handleApproveSubmit('APPROVED')}
            loading={submitting}
          >
            Chấp thuận & Ban hành Quyết định
          </Button>,
        ]}
      >
        <Form form={approveForm} layout="vertical" className="mt-4">
          <div className="p-3 bg-slate-50 border rounded-lg mb-4 text-xs space-y-1">
            <div><strong>Nhân sự:</strong> {selectedAppointment?.ho_ten} ({selectedAppointment?.ma_nv})</div>
            <div><strong>Vị trí bổ nhiệm:</strong> {selectedAppointment?.chuc_vu_moi} - {selectedAppointment?.ma_pb_moi}</div>
            <div><strong>Lý do:</strong> {selectedAppointment?.ly_do}</div>
          </div>
          <Form.Item name="comment" label="Ý kiến Lãnh đạo phê duyệt">
            <Input.TextArea rows={3} placeholder="Nhập nhận xét hoặc chỉ đạo thi hành..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AppointmentPage;
