import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, DatePicker, message, Row, Col, Space } from 'antd';
import { PlusOutlined, ProjectOutlined } from '@ant-design/icons';
import catalogApi from '../../api/catalogApi';
import { useAuth } from '../../context/AuthContext';

export const ProjectsPage = () => {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  const isGeneralDirector = user?.role_id === 4;
  const isHR = user?.department_name?.toLowerCase().includes('nhân sự') || user?.role_id === 2;
  const canCreate = isGeneralDirector || isHR;

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const res = await catalogApi.getProjects();
      if (res && res.data) {
        setProjects(Array.isArray(res.data) ? res.data : res.data.items || []);
      }
    } catch (err) {
      console.error('Fetch projects error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      const payload = {
        ma_du_an: Number(values.ma_du_an),
        ten_du_an: values.ten_du_an,
        ngay_bat_dau: values.ngay_bat_dau ? values.ngay_bat_dau.format('YYYY-MM-DD') : null,
        ngay_ket_thuc: values.ngay_ket_thuc ? values.ngay_ket_thuc.format('YYYY-MM-DD') : null,
      };
      await catalogApi.createProject(payload);
      message.success('Thêm dự án mới và đồng bộ 3 sites thành công!');
      setIsModalOpen(false);
      form.resetFields();
      fetchProjects();
    } catch (err) {
      console.error('Create project error:', err);
    }
  };

  const columns = [
    {
      title: 'Mã Dự Án',
      dataIndex: 'ma_du_an',
      key: 'ma_du_an',
      render: (val, r) => <span className="font-mono font-semibold">{val || r.MaDuAn}</span>,
    },
    {
      title: 'Tên Dự Án',
      dataIndex: 'ten_du_an',
      key: 'ten_du_an',
      render: (val, r) => <span className="font-semibold text-slate-800">{val || r.TenDuAn}</span>,
    },
    {
      title: 'Ngày Bắt Đầu',
      dataIndex: 'ngay_bat_dau',
      key: 'ngay_bat_dau',
      render: (val, r) => <span>{val || r.NgayBatDau || '—'}</span>,
    },
    {
      title: 'Ngày Kết Thúc',
      dataIndex: 'ngay_ket_thuc',
      key: 'ngay_ket_thuc',
      render: (val, r) => <span>{val || r.NgayKetThuc || '—'}</span>,
    },
  ];

  return (
    <div className="space-y-4">
      <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-lg font-bold text-slate-800">Danh mục Dự án Toàn tập đoàn (Replicated Table)</h2>
            <p className="text-xs text-slate-500">Dữ liệu dự án được nhân bản đồng bộ trên cả 3 sites: HN, DN, HCM</p>
          </div>
          {canCreate && (
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setIsModalOpen(true)}
              className="bg-blue-600"
            >
              Thêm Dự Án Mới
            </Button>
          )}
        </div>
      </Card>

      <Table
        columns={columns}
        dataSource={projects}
        rowKey={(r) => r.ma_du_an || r.MaDuAn || Math.random()}
        loading={loading}
        className="border border-slate-200 rounded-lg overflow-hidden bg-white shadow-sm"
      />

      <Modal
        title="Thêm mới Dự án (Đồng bộ 3 Shards)"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={handleCreate}
        okText="Tạo dự án"
        cancelText="Hủy"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="ma_du_an" label="Mã dự án (Số)" rules={[{ required: true }]}>
            <Input placeholder="VD: 104" type="number" />
          </Form.Item>
          <Form.Item name="ten_du_an" label="Tên dự án" rules={[{ required: true }]}>
            <Input placeholder="VD: Falcon Heavy Payload Test" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="ngay_bat_dau" label="Ngày bắt đầu">
                <DatePicker className="w-full" format="YYYY-MM-DD" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="ngay_ket_thuc" label="Ngày kết thúc">
                <DatePicker className="w-full" format="YYYY-MM-DD" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default ProjectsPage;
