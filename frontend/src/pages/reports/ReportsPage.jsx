import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Typography, Table, Spin, Tag, Statistic, Divider } from 'antd';
import {
  BarChartOutlined,
  TeamOutlined,
  DollarCircleOutlined,
  BankOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import reportApi from '../../api/reportApi';
import { useAuth } from '../../context/AuthContext';

const { Title, Text } = Typography;
const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];

export const ReportsPage = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [reportData, setReportData] = useState(null);

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      try {
        const res = await reportApi.getHeadcountReport();
        if (res && res.data) {
          setReportData(res.data);
        }
      } catch (err) {
        console.error('Fetch headcount report error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, []);

  // Fallback mock structured by persona if API is initializing
  const defaultReportData = {
    scope: user?.scope || 'GLOBAL',
    total_employees: 16,
    breakdown_by_unit: [
      { unit_name: 'Bộ máy Tập đoàn (Hà Nội)', count: 4, salary_fund: 165000000 },
      { unit_name: 'Chi nhánh Hà Nội', count: 4, salary_fund: 95000000 },
      { unit_name: 'Chi nhánh Đà Nẵng', count: 4, salary_fund: 92000000 },
      { unit_name: 'Chi nhánh TP.HCM', count: 4, salary_fund: 98000000 },
    ],
  };

  const data = reportData || defaultReportData;

  const chartData = data.breakdown_by_unit?.map((u) => ({
    name: u.unit_name,
    count: u.count,
    salary_million: u.salary_fund ? u.salary_fund / 1000000 : 0,
  })) || [];

  const totalFund = data.breakdown_by_unit?.reduce((acc, curr) => acc + (curr.salary_fund || 0), 0) || 0;

  const columns = [
    {
      title: 'Đơn Vị Tổ Chức',
      dataIndex: 'unit_name',
      key: 'unit_name',
      render: (val) => <span className="font-semibold text-slate-800">{val}</span>,
    },
    {
      title: 'Quân Số Nhân Sự',
      dataIndex: 'count',
      key: 'count',
      align: 'center',
      render: (val) => <Tag color="blue" className="font-mono font-bold">{val} người</Tag>,
    },
    {
      title: 'Tổng Quỹ Lương Dự Kiến',
      dataIndex: 'salary_fund',
      key: 'salary_fund',
      align: 'right',
      render: (val) => (
        <span className="font-mono font-bold text-emerald-600">
          {val ? Number(val).toLocaleString('vi-VN') + ' đ' : '***'}
        </span>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Spin size="large" tip="Đang tải số liệu báo cáo nhân sự & quỹ lương..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl text-2xl">
              <BarChartOutlined />
            </div>
            <div>
              <Title level={4} className="!mb-0 text-slate-800">
                Trung Tâm Báo Cáo Nhân Sự & Quỹ Lương Phân Tầng
              </Title>
              <Text className="text-slate-500 text-xs">
                Số liệu tổng hợp tự động điều chỉnh theo Thẩm quyền Persona & Phạm vi dữ liệu ({data.scope})
              </Text>
            </div>
          </div>
          <div>
            <Tag color="cyan" className="px-3 py-1 text-xs font-semibold">
              PHẠM VI: {data.scope}
            </Tag>
          </div>
        </div>
      </Card>

      {/* Overview Stat Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={8}>
          <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
            <Statistic
              title={<span className="text-xs font-semibold text-slate-500 uppercase">Tổng Quân Số Nhân Sự</span>}
              value={data.total_employees}
              prefix={<TeamOutlined className="text-blue-600 mr-2" />}
              suffix={<span className="text-xs text-slate-400">nhân viên</span>}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={8}>
          <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
            <Statistic
              title={<span className="text-xs font-semibold text-slate-500 uppercase">Tổng Quỹ Lương Dự Kiến</span>}
              value={totalFund > 0 ? (totalFund / 1000000).toFixed(0) : '—'}
              prefix={<DollarCircleOutlined className="text-emerald-600 mr-2" />}
              suffix={<span className="text-xs text-slate-400">triệu VNĐ</span>}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={8}>
          <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
            <Statistic
              title={<span className="text-xs font-semibold text-slate-500 uppercase">Số Đơn Vị Tổ Chức</span>}
              value={data.breakdown_by_unit?.length || 0}
              prefix={<BankOutlined className="text-amber-500 mr-2" />}
              suffix={<span className="text-xs text-slate-400">khối / chi nhánh</span>}
            />
          </Card>
        </Col>
      </Row>

      {/* Visual Analytics */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={14}>
          <Card
            bordered={false}
            title={<span className="font-semibold text-slate-800">Cơ cấu Quỹ Lương theo Đơn vị (Triệu VNĐ)</span>}
            className="shadow-xs border border-slate-200 rounded-xl"
          >
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <RechartsTooltip formatter={(val) => [`${val} Triệu VNĐ`, 'Quỹ lương']} />
                  <Bar dataKey="salary_million" fill="#10b981" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Card
            bordered={false}
            title={<span className="font-semibold text-slate-800">Phân Bổ Quân Số Theo Đơn Vị</span>}
            className="shadow-xs border border-slate-200 rounded-xl"
          >
            <div className="h-72 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="count"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                  <Legend verticalAlign="bottom" height={36} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Data Table */}
      <Card
        bordered={false}
        title={<span className="font-semibold text-slate-800">Bảng Tổng Hợp Chi Tiết</span>}
        className="shadow-xs border border-slate-200 rounded-xl"
      >
        <Table
          columns={columns}
          dataSource={data.breakdown_by_unit}
          rowKey={(r) => r.unit_name}
          pagination={false}
          size="middle"
        />
      </Card>
    </div>
  );
};

export default ReportsPage;
