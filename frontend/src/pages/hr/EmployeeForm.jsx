import React, { useState, useEffect } from 'react';
import {
  Drawer,
  Form,
  Input,
  Select,
  DatePicker,
  Button,
  Space,
  Row,
  Col,
  Divider,
  message,
} from 'antd';
import dayjs from 'dayjs';
import catalogApi from '../../api/catalogApi';
import employeeApi from '../../api/employeeApi';
import FileUploader from '../../components/FileUploader';
import JsonProfileForm from '../../components/JsonProfileForm';

const { Option } = Select;

export const EmployeeForm = ({
  visible,
  onClose,
  onSuccess,
  initialData = null,
  currentUser,
}) => {
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);

  // Catalogs
  const [departments, setDepartments] = useState([]);
  const [positions, setPositions] = useState([]);
  const [roles, setRoles] = useState([]);

  // File states for MinIO upload
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [cvFile, setCvFile] = useState(null);

  const isEdit = !!initialData;

  useEffect(() => {
    const fetchCatalogs = async () => {
      try {
        const [deptRes, posRes, roleRes] = await Promise.allSettled([
          catalogApi.getDepartments(),
          catalogApi.getPositions(),
          catalogApi.getRoles(),
        ]);

        if (deptRes.status === 'fulfilled' && deptRes.value?.data) {
          setDepartments(deptRes.value.data);
        }
        if (posRes.status === 'fulfilled' && posRes.value?.data) {
          setPositions(posRes.value.data);
        }
        if (roleRes.status === 'fulfilled' && roleRes.value?.data) {
          setRoles(roleRes.value.data);
        }
      } catch (err) {
        console.error('Fetch catalogs error:', err);
      }
    };

    fetchCatalogs();
  }, []);

  useEffect(() => {
    if (initialData) {
      form.setFieldsValue({
        ma_nv: initialData.ma_nv,
        ho_ten: initialData.ho_ten,
        phai: initialData.phai || 'Nam',
        ngay_sinh: initialData.ngay_sinh ? dayjs(initialData.ngay_sinh) : null,
        so_dien_thoai: initialData.so_dien_thoai,
        email: initialData.email,
        ma_so_thue: initialData.ma_so_thue,
        ma_pb: initialData.ma_pb,
        ma_cv: initialData.ma_cv,
        ma_vai_tro: initialData.ma_vai_tro || 1,
        ma_cn: initialData.chi_nhanh || initialData.ma_cn || 'HN',
        username: initialData.username || '',
        skills: initialData.skills || [],
        performance_reviews: initialData.performance_reviews || [],
      });
      setAvatarPreview(initialData.url_avatar || null);
    } else {
      form.resetFields();
      form.setFieldsValue({
        phai: 'Nam',
        ma_cn: currentUser?.branch || 'HN',
        ma_vai_tro: 1,
        ma_cv: 'NV',
        skills: [{ name: 'React', level: 'Intermediate' }],
        performance_reviews: [{ period: '2026-Q1', final_grade: 'B', feedback: 'Hoàn thành tốt công việc' }],
      });
      setAvatarFile(null);
      setAvatarPreview(null);
      setCvFile(null);
    }
  }, [initialData, form, currentUser]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);

      const payloadData = {
        ma_nv: values.ma_nv,
        ho_ten: values.ho_ten,
        phai: values.phai,
        ngay_sinh: values.ngay_sinh ? values.ngay_sinh.format('YYYY-MM-DD') : null,
        so_dien_thoai: values.so_dien_thoai,
        email: values.email,
        ma_so_thue: values.ma_so_thue,
        ma_pb: values.ma_pb,
        ma_cv: values.ma_cv,
        ma_vai_tro: values.ma_vai_tro,
        ma_cn: values.ma_cn,
        username: values.username || values.ma_nv?.toLowerCase(),
        password: values.password || 'Password123',
        skills: values.skills || [],
        performance_reviews: values.performance_reviews || [],
      };

      // Construct multipart form-data
      const formData = new FormData();
      formData.append('data', JSON.stringify(payloadData));

      if (avatarFile) {
        formData.append('avatar', avatarFile);
      }
      if (cvFile) {
        formData.append('cv_pdf', cvFile);
      }

      if (isEdit) {
        await employeeApi.update(initialData.ma_nv, formData);
        message.success(`Cập nhật hồ sơ nhân sự ${values.ma_nv} thành công!`);
      } else {
        await employeeApi.create(formData);
        message.success(`Thêm mới nhân sự ${values.ma_nv} thành công!`);
      }

      onSuccess();
    } catch (err) {
      console.error('Submit employee error:', err);
      // Handled by axiosClient message
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Drawer
      title={
        <span className="font-bold text-slate-800">
          {isEdit ? `Cập nhật Hồ sơ Nhân sự: ${initialData?.ma_nv}` : 'Thêm mới Hồ sơ Nhân sự Đa mô hình'}
        </span>
      }
      width={720}
      open={visible}
      onClose={onClose}
      extra={
        <Space>
          <Button onClick={onClose}>Hủy</Button>
          <Button type="primary" onClick={handleSubmit} loading={submitting} className="bg-blue-600">
            {isEdit ? 'Lưu thay đổi' : 'Tạo mới nhân sự'}
          </Button>
        </Space>
      }
    >
      <Form form={form} layout="vertical" requiredMark="optional">
        {/* Step 1: Upload Avatar & CV */}
        <Divider orientation="left" className="!text-sm !font-bold !text-blue-700">
          1. Đính kèm Đa phương tiện MinIO S3
        </Divider>
        <FileUploader
          avatarFile={avatarFile}
          setAvatarFile={setAvatarFile}
          avatarPreview={avatarPreview}
          setAvatarPreview={setAvatarPreview}
          cvFile={cvFile}
          setCvFile={setCvFile}
          currentAvatarUrl={initialData?.url_avatar}
          currentCvUrl={initialData?.url_cv}
        />

        {/* Step 2: Administrative info */}
        <Divider orientation="left" className="!text-sm !font-bold !text-blue-700 mt-6">
          2. Thông tin Hành chính & Phân tán
        </Divider>

        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="ma_nv"
              label="Mã nhân viên"
              rules={[{ required: true, message: 'Nhập mã NV (VD: NV_DN_02)' }]}
            >
              <Input placeholder="NV_DN_02" disabled={isEdit} />
            </Form.Item>
          </Col>
          <Col span={10}>
            <Form.Item
              name="ho_ten"
              label="Họ và tên"
              rules={[{ required: true, message: 'Nhập họ tên đầy đủ' }]}
            >
              <Input placeholder="Nguyễn Văn A" />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item name="phai" label="Giới tính">
              <Select>
                <Option value="Nam">Nam</Option>
                <Option value="Nữ">Nữ</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="ma_cn"
              label="Chi nhánh (Shard Sharding)"
              rules={[{ required: true, message: 'Chọn chi nhánh' }]}
            >
              <Select placeholder="Chọn chi nhánh" disabled={isEdit}>
                <Option value="HN">Hà Nội (site_hn)</Option>
                <Option value="DN">Đà Nẵng (site_dn)</Option>
                <Option value="HCM">TP.HCM (site_hcm)</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="ma_pb"
              label="Phòng ban"
              rules={[{ required: true, message: 'Chọn phòng ban' }]}
            >
              <Select placeholder="Chọn phòng ban">
                {departments.length > 0 ? (
                  departments.map((d) => (
                    <Option key={d.ma_pb || d.MaPB} value={d.ma_pb || d.MaPB}>
                      {d.ten_pb || d.TenPB} ({d.ma_cn || d.MaCN})
                    </Option>
                  ))
                ) : (
                  <>
                    <Option value="PB_HN_01">Phòng Quản Trị Trung Tâm (HN)</Option>
                    <Option value="PB_HN_02">Phòng Nhân Sự (HN)</Option>
                    <Option value="PB_HN_03">Phòng Tài Vụ (HN)</Option>
                    <Option value="PB_DN_01">Phòng Kỹ Thuật (DN)</Option>
                    <Option value="PB_HCM_01">Phòng Kinh Doanh (HCM)</Option>
                  </>
                )}
              </Select>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="ma_cv"
              label="Chức vụ"
              rules={[{ required: true, message: 'Chọn chức vụ' }]}
            >
              <Select placeholder="Chọn chức vụ">
                {positions.length > 0 ? (
                  positions.map((p) => (
                    <Option key={p.ma_cv || p.MaCV} value={p.ma_cv || p.MaCV}>
                      {p.ten_cv || p.TenCV} (Hệ số: {p.he_so_luong || p.HeSoLuong})
                    </Option>
                  ))
                ) : (
                  <>
                    <Option value="TGD">Tổng giám đốc (4.0)</Option>
                    <Option value="GD">Giám đốc (3.0)</Option>
                    <Option value="TP">Trưởng phòng (1.5)</Option>
                    <Option value="NV">Nhân viên (1.0)</Option>
                  </>
                )}
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={8}>
            <Form.Item name="ma_vai_tro" label="Vai trò hệ thống (RBAC)">
              <Select placeholder="Chọn vai trò">
                <Option value={4}>Tổng giám đốc (Cấp 4)</Option>
                <Option value={3}>Giám đốc (Cấp 3)</Option>
                <Option value={2}>Trưởng phòng (Cấp 2)</Option>
                <Option value={1}>Nhân viên (Cấp 1)</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="email"
              label="Địa chỉ Email"
              rules={[{ required: true, type: 'email', message: 'Email không hợp lệ' }]}
            >
              <Input placeholder="email@x.corp" />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item name="so_dien_thoai" label="Số điện thoại">
              <Input placeholder="0905xxxxxx" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={8}>
            <Form.Item name="ngay_sinh" label="Ngày sinh">
              <DatePicker format="YYYY-MM-DD" className="w-full" />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item name="ma_so_thue" label="Mã số thuế">
              <Input placeholder="MST_DN_01" />
            </Form.Item>
          </Col>
          {!isEdit && (
            <Col span={8}>
              <Form.Item name="password" label="Mật khẩu khởi tạo">
                <Input.Password placeholder="Password123" />
              </Form.Item>
            </Col>
          )}
        </Row>

        {/* Step 3: JSON Profile Form */}
        <Divider orientation="left" className="!text-sm !font-bold !text-blue-700 mt-6">
          3. Dữ liệu Bán cấu trúc JSONB (Skills & KPI)
        </Divider>
        <JsonProfileForm />
      </Form>
    </Drawer>
  );
};

export default EmployeeForm;
