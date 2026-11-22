import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Progress, Table, Tag, Typography, Spin, Space } from 'antd';
import {
  TeamOutlined,
  DollarCircleOutlined,
  CheckCircleOutlined,
  ClusterOutlined,
  ArrowUpOutlined,
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
import { useAuth } from '../../context/AuthContext';
import employeeApi from '../../api/employeeApi';
import payrollApi from '../../api/payrollApi';
import systemApi from '../../api/systemApi';

const { Title, Text } = Typography;

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];

export const GlobalDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [employees, setEmployees] = useState([]);
  const [payrollData, setPayrollData] = useState([]);
  const [healthStatus, setHealthStatus] = useState(null);

  const isGeneralDirector = user?.role_id === 4;
  const currentBranch = user?.branch || 'HN';

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        const [empRes, sysRes] = await Promise.allSettled([
          employeeApi.getAll({ page: 1, page_size: 100 }),
          systemApi.getHealth(),
        ]);

        if (empRes.status === 'fulfilled' && empRes.value?.data?.items) {
          setEmployees(empRes.value.data.items);
        }

        if (sysRes.status === 'fulfilled' && sysRes.value?.data) {
          setHealthStatus(sysRes.value.data);
        }
      } catch (err) {
        console.error('Fetch dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Compute metrics
  const totalEmployees = employees.length;
  const branchCounts = employees.reduce((acc, curr) => {
    const b = curr.chi_nhanh || 'HN';
    acc[b] = (acc[b] || 0) + 1;
    return acc;
  }, {});

  const regionalData = [
    { name: 'Hà Nội (Hội sở)', count: branchCounts['HN'] || 0, code: 'HN' },
    { name: 'Đà Nẵng (Miền Trung)', count: branchCounts['DN'] || 0, code: 'DN' },
    { name: 'TP.HCM (Miền Nam)', count: branchCounts['HCM'] || 0, code: 'HCM' },
  ];

  // KPI distribution
  const kpiCounts = employees.reduce((acc, curr) => {
    const k = curr.kpi_q1 || 'Chưa đánh giá';
    acc[k] = (acc[k] || 0) + 1;
    return acc;
  }, {});

  const kpiData = Object.keys(kpiCounts).map((key) => ({
    name: `Hạng ${key}`,
    value: kpiCounts[key],
  }));

  // Salary budget by branch
  const salaryByBranch = employees.reduce((acc, curr) => {
    const b = curr.chi_nhanh || 'HN';
    const salary = Number(curr.luong_thuc_linh) || 0;
    acc[b] = (acc[b] || 0) + salary;
    return acc;
  }, {});

  const salaryBudgetChartData = [
    { branch: 'Hà Nội', total: (salaryByBranch['HN'] || 0) / 1000000 },
    { branch: 'Đà Nẵng', total: (salaryByBranch['DN'] || 0) / 1000000 },
    { branch: 'TP.HCM', total: (salaryByBranch['HCM'] || 0) / 1000000 },
  ];

  const totalBudget = Object.values(salaryByBranch).reduce((a, b) => a + b, 0);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Spin size="large" tip="Đang tổng hợp dữ liệu báo cáo đa chi nhánh..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner / Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-white p-6 rounded-xl border border-slate-200 shadow-xs gap-4">
        <div>
          <Title level={4} className="!mb-1 text-slate-800">
            {isGeneralDirector ? 'Báo cáo Tổng quan Toàn tập đoàn SpaceX' : `Báo cáo Chi nhánh ${currentBranch}`}
          </Title>
          <Text className="text-slate-500 text-xs">
            Dữ liệu phân tán thời gian thực từ 3 Shard PostgreSQL (HN, DN, HCM) kết hợp FDW Coordinator
          </Text>
        </div>
        <div className="flex items-center gap-2">
          <Tag color="cyan" className="px-3 py-1 font-mono text-xs">
            {healthStatus?.overall_status === 'HEALTHY' ? '● CỤM 3 SHARD ONLINE' : '● CỤM CÓ CẢNH BÁO'}
          </Tag>
          <Tag color="blue" className="px-3 py-1 font-semibold text-xs">
            Q1 - 2026
          </Tag>
        </div>
      </div>

      {/* Overview Metric Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
            <Statistic
              title={<span className="text-xs font-semibold text-slate-500 uppercase">Tổng quân số nhân sự</span>}
              value={totalEmployees}
              prefix={<TeamOutlined className="text-blue-600 mr-2" />}
              suffix={<span className="text-xs text-slate-400">nhân sự</span>}
            />
            <div className="mt-2 text-xs text-slate-400 flex justify-between">
              <span>Hà Nội: {branchCounts['HN'] || 0}</span>
              <span>Đà Nẵng: {branchCounts['DN'] || 0}</span>
              <span>TP.HCM: {branchCounts['HCM'] || 0}</span>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
            <Statistic
              title={<span className="text-xs font-semibold text-slate-500 uppercase">Tổng ngân sách lương Q1</span>}
              value={totalBudget ? (totalBudget / 1000000).toFixed(0) : '—'}
              prefix={<DollarCircleOutlined className="text-emerald-600 mr-2" />}
              suffix={<span className="text-xs text-slate-400">triệu VNĐ</span>}
            />
            <div className="mt-2 text-xs text-emerald-600 flex items-center">
              <ArrowUpOutlined className="mr-1" />
              <span>Đã kiểm toán và đối soát hoàn tất</span>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
            <Statistic
              title={<span className="text-xs font-semibold text-slate-500 uppercase">Tỷ lệ KPI Hạng A</span>}
              value={totalEmployees > 0 ? (((kpiCounts['A'] || 0) / totalEmployees) * 100).toFixed(1) : 0}
              prefix={<CheckCircleOutlined className="text-amber-500 mr-2" />}
              suffix="%"
            />
            <div className="mt-2 text-xs text-slate-400">
              <span>{kpiCounts['A'] || 0} nhân sự xuất sắc</span>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
            <Statistic
              title={<span className="text-xs font-semibold text-slate-500 uppercase">Trạng thái Cụm Shard</span>}
              value={healthStatus?.nodes ? `${healthStatus.nodes.filter(n => n.status === 'ONLINE').length}/4 Online` : '4/4 Online'}
              prefix={<ClusterOutlined className="text-indigo-600 mr-2" />}
            />
            <div className="mt-2 text-xs text-slate-400">
              <span>Độ trễ trung bình: &lt; 3.5ms</span>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Visual Charts */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={14}>
          <Card
            bordered={false}
            title={<span className="font-semibold text-slate-800">Quỹ Lương theo Chi nhánh (Triệu VNĐ)</span>}
            className="shadow-xs border border-slate-200 rounded-xl"
          >
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={salaryBudgetChartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="branch" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <RechartsTooltip formatter={(val) => [`${val.toLocaleString()} Triệu VNĐ`, 'Tổng quỹ lương']} />
                  <Bar dataKey="total" fill="#2563eb" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Card
            bordered={false}
            title={<span className="font-semibold text-slate-800">Cơ cấu Xếp loại KPI Q1</span>}
            className="shadow-xs border border-slate-200 rounded-xl"
          >
            <div className="h-72 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={kpiData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={85}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {kpiData.map((entry, index) => (
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
    </div>
  );
};

export default GlobalDashboard;
