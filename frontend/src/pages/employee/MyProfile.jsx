import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Descriptions,
  Avatar,
  Tag,
  Typography,
  Table,
  Spin,
  Button,
  Divider,
} from 'antd';
import {
  UserOutlined,
  DollarCircleOutlined,
  FilePdfOutlined,
  TeamOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';
import employeeApi from '../../api/employeeApi';
import payrollApi from '../../api/payrollApi';

const { Title, Text } = Typography;

export const MyProfile = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [profileData, setProfileData] = useState(null);
  const [salarySlip, setSalarySlip] = useState(null);
  const [colleagues, setColleagues] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const maNv = user?.ma_nv;
        const [empRes, slipRes, colRes] = await Promise.allSettled([
          maNv ? employeeApi.getById(maNv) : Promise.reject('No ma_nv'),
          payrollApi.getMySlip({ month: 3, year: 2026 }),
          employeeApi.getColleagues(),
        ]);

        if (empRes.status === 'fulfilled' && empRes.value?.data) {
          setProfileData(empRes.value.data);
        }
        if (slipRes.status === 'fulfilled' && slipRes.value?.data) {
          setSalarySlip(slipRes.value.data);
        }
        if (colRes.status === 'fulfilled' && colRes.value?.data) {
          setColleagues(colRes.value.data.items || colRes.value.data || []);
        }
      } catch (err) {
        console.error('Fetch profile error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Spin size="large" tip="Đang tải dữ liệu hồ sơ cá nhân..." />
      </div>
    );
  }

  const colleagueColumns = [
    {
      title: 'Họ và tên',
      key: 'name',
      render: (_, r) => (
        <div className="flex items-center gap-2">
          <Avatar src={r.url_avatar} icon={<UserOutlined />} size="small" />
          <span className="font-semibold text-slate-800">{r.ho_ten}</span>
        </div>
      ),
    },
    {
      title: 'Chức vụ',
      dataIndex: 'chuc_vu',
      key: 'chuc_vu',
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Lương',
      key: 'salary',
      render: () => <Tag color="default">Bảo mật</Tag>,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Profile Card */}
      <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl overflow-hidden">
        <div className="flex flex-col md:flex-row items-start md:items-center gap-6 p-2">
          <Avatar
            src={profileData?.url_avatar}
            icon={<UserOutlined />}
            size={100}
            className="border-2 border-blue-500 shadow-md flex-shrink-0"
          />
          <div className="flex-1 space-y-2">
            <div className="flex flex-wrap items-center gap-3">
              <Title level={3} className="!mb-0 text-slate-800">
                {profileData?.ho_ten || user?.full_name}
              </Title>
              <Tag color="blue" className="font-semibold">
                {user?.branch || 'HN'}
              </Tag>
              <Tag color="cyan">{user?.role_name || 'Nhân viên'}</Tag>
            </div>
            <div className="text-slate-500 text-sm">
              Mã nhân viên: <span className="font-mono font-semibold text-slate-700">{user?.ma_nv}</span> •{' '}
              {user?.department_name}
            </div>
            <div className="flex gap-4 pt-1">
              {profileData?.url_cv && (
                <a
                  href={profileData.url_cv}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs text-blue-600 hover:underline"
                >
                  <FilePdfOutlined className="text-rose-500" /> Xem tệp CV Scan (MinIO)
                </a>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Row gutter={[16, 16]}>
        {/* Left Column: Personal info & Skills */}
        <Col xs={24} lg={14} className="space-y-6">
          <Card
            bordered={false}
            title={<span className="font-semibold text-slate-800">Thông tin Hành chính</span>}
            className="shadow-xs border border-slate-200 rounded-xl"
          >
            <Descriptions size="middle" column={2} bordered>
              <Descriptions.Item label="Email">{profileData?.email || '—'}</Descriptions.Item>
              <Descriptions.Item label="Số điện thoại">{profileData?.so_dien_thoai || '—'}</Descriptions.Item>
              <Descriptions.Item label="Giới tính">{profileData?.phai || '—'}</Descriptions.Item>
              <Descriptions.Item label="Ngày sinh">{profileData?.ngay_sinh || '—'}</Descriptions.Item>
              <Descriptions.Item label="Mã số thuế">{profileData?.ma_so_thue || '—'}</Descriptions.Item>
              <Descriptions.Item label="Trạng thái">
                <Tag color="green">{profileData?.trang_thai || 'DangLamViec'}</Tag>
              </Descriptions.Item>
            </Descriptions>
          </Card>

          <Card
            bordered={false}
            title={<span className="font-semibold text-slate-800">Hồ sơ Năng lực (JSONB Skills)</span>}
            className="shadow-xs border border-slate-200 rounded-xl"
          >
            <div className="flex flex-wrap gap-2">
              {profileData?.skills && Array.isArray(profileData.skills) && profileData.skills.length > 0 ? (
                profileData.skills.map((skill, idx) => (
                  <Tag key={idx} color="geekblue" className="px-3 py-1 text-xs">
                    <strong>{skill.name}</strong> • {skill.level}
                  </Tag>
                ))
              ) : (
                <Text type="secondary">Chưa có kỹ năng ghi nhận.</Text>
              )}
            </div>
          </Card>

          <Card
            bordered={false}
            title={<span className="font-semibold text-slate-800">Đồng nghiệp cùng Phòng ban</span>}
            className="shadow-xs border border-slate-200 rounded-xl"
          >
            <Table
              columns={colleagueColumns}
              dataSource={colleagues}
              rowKey={(r) => r.ma_nv}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>

        {/* Right Column: Salary Slip */}
        <Col xs={24} lg={10}>
          <Card
            bordered={false}
            title={
              <div className="flex items-center gap-2 text-slate-800">
                <DollarCircleOutlined className="text-emerald-600" />
                <span className="font-semibold">Phiếu Lương Kỳ Gần Nhất (03/2026)</span>
              </div>
            }
            className="shadow-xs border border-slate-200 rounded-xl bg-gradient-to-br from-white to-slate-50"
          >
            {salarySlip ? (
              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-100 p-4 rounded-xl text-center">
                  <div className="text-xs font-semibold text-blue-600 uppercase">Thực lĩnh nhận về</div>
                  <div className="text-3xl font-extrabold text-blue-700 font-mono mt-1">
                    {Number(salarySlip.luong_thuc_linh || 0).toLocaleString('vi-VN')} đ
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-500">Lương cơ bản</span>
                    <span className="font-mono font-semibold">
                      {Number(salarySlip.luong_co_ban || 0).toLocaleString('vi-VN')} đ
                    </span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-500">Phụ cấp</span>
                    <span className="font-mono font-semibold">
                      +{Number(salarySlip.phu_cap || 0).toLocaleString('vi-VN')} đ
                    </span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-500">Thưởng KPI</span>
                    <span className="font-mono font-semibold text-emerald-600">
                      +{Number(salarySlip.thuong || 0).toLocaleString('vi-VN')} đ
                    </span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-500">Khấu trừ thuế & bảo hiểm</span>
                    <span className="font-mono font-semibold text-rose-500">
                      -{Number(salarySlip.khau_tru || 0).toLocaleString('vi-VN')} đ
                    </span>
                  </div>
                </div>

                <div className="text-[11px] text-slate-400 text-center italic mt-4">
                  Bảo mật thông tin thu nhập theo Quy định Bảo mật Nội bộ SpaceX HRM
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-slate-400">
                Chưa có dữ liệu phiếu lương cho kỳ này.
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default MyProfile;
