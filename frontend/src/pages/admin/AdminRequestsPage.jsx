import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Tag,
  Typography,
  Space,
  Row,
  Col,
  Alert,
  message,
} from 'antd';
import {
  ToolOutlined,
  PlusOutlined,
  CheckOutlined,
  CloseOutlined,
  ReloadOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons';
import adminRequestApi from '../../api/adminRequestApi';
import { useAuth } from '../../context/AuthContext';

const { Title, Text } = Typography;
const { Option } = Select;

export const AdminRequestsPage = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [requests, setRequests] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [approveModalOpen, setApproveModalOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const [form] = Form.useForm();
  const [approveForm] = Form.useForm();

  const isCEO = user?.role_id === 4 || user?.position === 'CEO' || user?.position === 'TGD';
  const isBranchDirector = user?.role_id === 3 || user?.position === 'GD_CN' || user?.position === 'GD';
  const isOps = user?.department_name?.toLowerCase().includes('vận hành') || user?.department_id?.includes('OPS');

  const canRequest = isOps;
  const canApprove = isCEO || isBranchDirector;

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const res = await adminRequestApi.getAdminRequests();
      if (res && res.data) {
        setRequests(Array.isArray(res.data) ? res.data : res.data.items || []);
      }
    } catch (err) {
      console.error('Fetch admin requests error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);
      const payload = {
        loai_yeu_cau: values.loai_yeu_cau,
        pham_vi: values.pham_vi,
        chi_nhanh: values.chi_nhanh || user?.branch || 'HN',
        ly_do: values.ly_do,
        thong_so_ky_thuat: {
          node_target: values.node_target || 'site_hn',
          duration_hours: Number(values.duration_hours) || 24,
        },
      };

      await adminRequestApi.createAdminRequest(payload);
      message.success('Đã gửi yêu cầu kỹ thuật! Chờ Lãnh đạo cấp thẩm quyền phê duyệt.');
      setIsModalOpen(false);
      form.resetFields();
      fetchRequests();
    } catch (err) {
      console.error('Create request error:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleApproveSubmit = async (decision) => {
    try {
      const values = await approveForm.validateFields();
      setSubmitting(true);
      const id = selectedRequest.id || selectedRequest.ma_yeu_cau;

      await adminRequestApi.approveAdminRequest(id, {
        decision,
        comment: values.comment || (decision === 'APPROVED' ? 'Chấp thuận cấp quyền kỹ thuật' : 'Từ chối'),
      });

      message.success(`Đã xử lý ${decision === 'APPROVED' ? 'CHẤP THUẬN' : 'TỪ CHỐI'} yêu cầu thành công!`);
      setApproveModalOpen(false);
      approveForm.resetFields();
      fetchRequests();
    } catch (err) {
      console.error('Approve request error:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    {
      title: 'Mã Yêu Cầu',
      dataIndex: 'ma_yeu_cau',
      key: 'ma_yeu_cau',
      render: (val, r) => <span className="font-mono font-semibold">{val || r.id}</span>,
    },
    {
      title: 'Loại Yêu Cầu',
      dataIndex: 'loai_yeu_cau',
      key: 'type',
      render: (val) => <Tag color="blue">{val}</Tag>,
    },
    {
      title: 'Người Yêu Cầu (Operator)',
      key: 'requester',
      render: (_, r) => (
        <div>
          <span className="font-semibold text-slate-800">{r.ten_nv_yeu_cau || r.ma_nv_yeu_cau}</span>
          <div className="text-xs text-slate-400 font-mono">Phòng Vận Hành • {r.chi_nhanh}</div>
        </div>
      ),
    },
    {
      title: 'Phạm vi & Node',
      key: 'scope',
      render: (_, r) => (
        <div>
          <Tag color={r.pham_vi === 'GLOBAL' ? 'gold' : 'cyan'}>{r.pham_vi}</Tag>
          <span className="text-xs font-mono text-slate-600">{r.thong_so_ky_thuat?.node_target || 'All Shards'}</span>
        </div>
      ),
    },
    {
      title: 'Lý do kỹ thuật',
      dataIndex: 'ly_do',
      key: 'ly_do',
      render: (val) => <span className="text-xs text-slate-600">{val}</span>,
    },
    {
      title: 'Trạng thái',
      dataIndex: 'trang_thai',
      key: 'status',
      render: (st) => {
        const s = st || 'PENDING';
        if (s === 'APPROVED') return <Tag color="success">ĐÃ PHÊ DUYỆT</Tag>;
        if (s === 'REJECTED') return <Tag color="error">TỪ CHỐI</Tag>;
        return <Tag color="processing">CHỜ DUYỆT</Tag>;
      },
    },
    {
      title: 'Thao tác',
      key: 'actions',
      render: (_, r) => {
        const isPending = (r.trang_thai || 'PENDING') === 'PENDING';
        const isSelf = r.ma_nv_yeu_cau === user?.ma_nv;

        if (!canApprove || !isPending) {
          return <span className="text-xs text-slate-400 italic">Đã kết thúc</span>;
        }

        // Anti-self approval rule check: Operator cannot approve their own request
        if (isSelf) {
          return (
            <Tag color="warning" className="text-xs">
              Chống tự duyệt
            </Tag>
          );
        }

        return (
          <Button
            type="primary"
            size="small"
            className="bg-blue-600"
            onClick={() => {
              setSelectedRequest(r);
              setApproveModalOpen(true);
            }}
          >
            Duyệt yêu cầu
          </Button>
        );
      },
    },
  ];

  return (
    <div className="space-y-4">
      {/* Top Banner */}
      <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl text-xl">
              <ToolOutlined />
            </div>
            <div>
              <Title level={4} className="!mb-0 text-slate-800">
                Quản trị Kỹ thuật có Phê duyệt (Technical Governance)
              </Title>
              <Text className="text-slate-500 text-xs">
                Phòng Vận hành (System Operator) gửi yêu cầu $\rightarrow$ Lãnh đạo thẩm quyền (Executive Approver) phê duyệt. Nghiêm cấm tự duyệt!
              </Text>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button icon={<ReloadOutlined />} onClick={fetchRequests}>
              Làm mới
            </Button>
            {canRequest && (
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setIsModalOpen(true)}
                className="bg-blue-600 font-semibold"
              >
                Tạo Yêu Cầu Kỹ Thuật
              </Button>
            )}
          </div>
        </div>
      </Card>

      <Alert
        message="Nguyên tắc Tách biệt & Quản trị An toàn (Separation of Concerns)"
        description="Quản trị kỹ thuật (System Operator) không có quyền can thiệp trái phép hồ sơ nhân sự và bảng lương. Mọi thao tác cấu hình nhạy cảm đều cần có sự chấp thuận của Lãnh đạo (CEO / Giám đốc CN)."
        type="info"
        showIcon
        className="rounded-xl border-blue-200 bg-blue-50/50"
      />

      <Table
        columns={columns}
        dataSource={requests}
        rowKey={(r) => r.id || r.ma_yeu_cau || Math.random()}
        loading={loading}
        className="border border-slate-200 rounded-lg overflow-hidden bg-white shadow-sm"
      />

      {/* Modal: Operator Create Request */}
      <Modal
        title="Tạo Yêu Cầu Cấp Quyền / Thao Tác Kỹ Thuật"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={handleCreate}
        confirmLoading={submitting}
        okText="Gửi yêu cầu"
        cancelText="Hủy"
        width={550}
      >
        <Form form={form} layout="vertical" className="mt-4">
          <Form.Item name="loai_yeu_cau" label="Loại yêu cầu" rules={[{ required: true }]}>
            <Select placeholder="Chọn loại yêu cầu">
              <Option value="CAP_QUYEN_OPERATOR">Cấp quyền Quản trị Operator tạm thời</Option>
              <Option value="BAO_TRI_HE_THONG">Bảo trì Nút CSDL định kỳ</Option>
              <Option value="KHOI_PHUC_NODE">Khôi phục & Đồng bộ dữ liệu Shard</Option>
              <Option value="XU_LY_SU_CO">Xử lý Sự cố & Graceful Degradation</Option>
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="pham_vi" label="Phạm vi tác động" rules={[{ required: true }]}>
                <Select placeholder="Chọn phạm vi">
                  <Option value="GLOBAL">Toàn tập đoàn (GLOBAL - CEO duyệt)</Option>
                  <Option value="BRANCH">Cục bộ Chi nhánh (BRANCH - Giám đốc CN duyệt)</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="node_target" label="Nút CSDL mục tiêu">
                <Select placeholder="Chọn node">
                  <Option value="site_hn">site_hn (Coordinator & Shard)</Option>
                  <Option value="site_dn">site_dn (Shard Đà Nẵng)</Option>
                  <Option value="site_hcm">site_hcm (Shard TP.HCM)</Option>
                  <Option value="minio_server">minio_server (S3 Object Storage)</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="duration_hours" label="Thời lượng yêu cầu (Giờ)">
            <Input type="number" placeholder="24" defaultValue={24} />
          </Form.Item>

          <Form.Item name="ly_do" label="Lý do kỹ thuật & Kế hoạch thao tác" rules={[{ required: true }]}>
            <Input.TextArea rows={3} placeholder="Mô tả mục đích bảo trì, thời gian downtime dự kiến (nếu có)..." />
          </Form.Item>
        </Form>
      </Modal>

      {/* Modal: Executive Approve/Reject */}
      <Modal
        title={`Phê Duyệt Quyền Kỹ Thuật: ${selectedRequest?.ma_yeu_cau}`}
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
            Chấp thuận & Cấp quyền
          </Button>,
        ]}
      >
        <Form form={approveForm} layout="vertical" className="mt-4">
          <div className="p-3 bg-slate-50 border rounded-lg mb-4 text-xs space-y-1">
            <div><strong>Người yêu cầu:</strong> {selectedRequest?.ten_nv_yeu_cau || selectedRequest?.ma_nv_yeu_cau}</div>
            <div><strong>Loại:</strong> {selectedRequest?.loai_yeu_cau}</div>
            <div><strong>Phạm vi:</strong> {selectedRequest?.pham_vi} • Node: {selectedRequest?.thong_so_ky_thuat?.node_target}</div>
            <div><strong>Lý do:</strong> {selectedRequest?.ly_do}</div>
          </div>
          <Form.Item name="comment" label="Chỉ đạo & Ghi chú phê duyệt">
            <Input.TextArea rows={3} placeholder="Ý kiến chỉ đạo hoặc yêu cầu giám sát..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AdminRequestsPage;
