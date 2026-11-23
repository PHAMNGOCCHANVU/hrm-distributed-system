import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, message } from 'antd';
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
        </Card>
      </div>
    </div>
  );
};

export default LoginPage;
