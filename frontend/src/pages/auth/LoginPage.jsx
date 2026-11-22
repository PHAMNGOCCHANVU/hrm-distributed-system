import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, Space, Divider, message } from 'antd';
import { UserOutlined, LockOutlined, RocketOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const { Title, Text } = Typography;

export const LoginPage = () => {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/';

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const user = await login(values.username, values.password);
      message.success(`Chào mừng ${user.full_name} (${user.role_name}) trở lại!`);
      // Redirect based on role
      if (user.role_id === 4 || user.role_id === 3) {
        navigate('/dashboard', { replace: true });
      } else if (user.department_name?.toLowerCase().includes('tài vụ')) {
        navigate('/payroll', { replace: true });
      } else if (user.department_name?.toLowerCase().includes('nhân sự')) {
        navigate('/employees', { replace: true });
      } else {
        navigate('/profile', { replace: true });
      }
    } catch (err) {
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (username, password) => {
    form.setFieldsValue({ username, password });
    onFinish({ username, password });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-600 text-white text-2xl shadow-lg mb-3">
            <RocketOutlined />
          </div>
          <Title level={2} className="!text-white !mb-1 tracking-tight">
            SpaceX HRM
          </Title>
          <Text className="text-slate-400 text-xs tracking-wider uppercase font-mono">
            Hệ thống Quản trị Nhân sự & Lương Phân tán
          </Text>
        </div>

        <Card className="shadow-2xl border-slate-700/50 rounded-2xl bg-white/95 backdrop-blur-sm">
          <Form
            form={form}
            name="login_form"
            layout="vertical"
            onFinish={onFinish}
            autoComplete="off"
            requiredMark={false}
          >
            <Form.Item
              name="username"
              label={<span className="text-xs font-semibold text-slate-700 uppercase">Tên đăng nhập</span>}
              rules={[{ required: true, message: 'Vui lòng nhập tên tài khoản!' }]}
            >
              <Input
                prefix={<UserOutlined className="text-slate-400 mr-1" />}
                placeholder="VD: giap_gd"
                size="large"
                className="rounded-lg"
              />
            </Form.Item>

            <Form.Item
              name="password"
              label={<span className="text-xs font-semibold text-slate-700 uppercase">Mật khẩu</span>}
              rules={[{ required: true, message: 'Vui lòng nhập mật khẩu!' }]}
            >
              <Input.Password
                prefix={<LockOutlined className="text-slate-400 mr-1" />}
                placeholder="Nhập mật khẩu"
                size="large"
                className="rounded-lg"
              />
            </Form.Item>

            <Form.Item className="mt-6 mb-2">
              <Button
                type="primary"
                htmlType="submit"
                size="large"
                block
                loading={loading}
                className="rounded-lg font-semibold bg-blue-600 hover:bg-blue-500 h-11"
              >
                Đăng nhập hệ thống
              </Button>
            </Form.Item>
          </Form>

          <Divider plain className="!my-4 !text-xs !text-slate-400">
            Tài khoản dùng thử một chạm (Mật khẩu: 123456)
          </Divider>

          <div className="grid grid-cols-1 gap-2">
            <Button
              size="small"
              className="text-left text-xs h-auto py-1.5 px-3 flex justify-between items-center hover:border-blue-500"
              onClick={() => handleQuickLogin('giap_gd', '123456')}
            >
              <span className="font-semibold text-slate-800">1. Tổng giám đốc (Lưu Quang Giáp - HN)</span>
              <span className="text-slate-400 font-mono text-[11px]">giap_gd</span>
            </Button>

            <Button
              size="small"
              className="text-left text-xs h-auto py-1.5 px-3 flex justify-between items-center hover:border-blue-500"
              onClick={() => handleQuickLogin('linh_hcm', '123456')}
            >
              <span className="font-semibold text-slate-800">2. Trưởng phòng (Trần Thị Mỹ Linh - HCM)</span>
              <span className="text-slate-400 font-mono text-[11px]">linh_hcm</span>
            </Button>

            <Button
              size="small"
              className="text-left text-xs h-auto py-1.5 px-3 flex justify-between items-center hover:border-blue-500"
              onClick={() => handleQuickLogin('cuong_dn', '123456')}
            >
              <span className="font-semibold text-slate-800">3. Nhân viên Kỹ thuật (Phạm Văn Cường - ĐN)</span>
              <span className="text-slate-400 font-mono text-[11px]">cuong_dn</span>
            </Button>

            <Button
              size="small"
              className="text-left text-xs h-auto py-1.5 px-3 flex justify-between items-center hover:border-blue-500"
              onClick={() => handleQuickLogin('hoa_nv', '123456')}
            >
              <span className="font-semibold text-slate-800">4. Nhân viên Quản trị (Nguyễn Thị Hoa - HN)</span>
              <span className="text-slate-400 font-mono text-[11px]">hoa_nv</span>
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default LoginPage;
