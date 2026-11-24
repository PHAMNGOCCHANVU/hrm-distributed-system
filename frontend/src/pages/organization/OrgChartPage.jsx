import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Typography, Spin, Tag, Tree, Divider, Badge } from 'antd';
import {
  ApartmentOutlined,
  CrownOutlined,
  BankOutlined,
  TeamOutlined,
  UserOutlined,
  ClusterOutlined,
} from '@ant-design/icons';
import organizationApi from '../../api/organizationApi';

const { Title, Text } = Typography;

export const OrgChartPage = () => {
  const [loading, setLoading] = useState(true);
  const [orgData, setOrgData] = useState(null);

  useEffect(() => {
    const fetchOrgTree = async () => {
      setLoading(true);
      try {
        const res = await organizationApi.getOrgTree();
        if (res && res.data) {
          setOrgData(res.data);
        }
      } catch (err) {
        console.error('Fetch org tree error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchOrgTree();
  }, []);

  // Fallback structural mock data matching Section 2.1 & 3.2 if API returns empty
  const defaultOrgData = {
    corporate_hq: {
      unit_name: 'Bộ Máy Điều Hành Cấp Tập Đoàn (Trụ sở Hà Nội)',
      leader: {
        position: 'CEO - Tổng giám đốc',
        full_name: 'Lưu Quang Giáp',
        ma_nv: 'NV_HQ_CEO',
      },
      departments: [
        { code: 'PB_HQ_ADMIN', name: 'Văn phòng Quản trị Tập đoàn', manager: 'Ngô Quang Minh' },
        { code: 'PB_HQ_HR', name: 'Phòng Nhân sự Tập đoàn', manager: 'Lê Thu Trang' },
        { code: 'PB_HQ_FIN', name: 'Phòng Tài chính Tập đoàn', manager: 'Đặng Thùy Dung' },
        { code: 'PB_HQ_OPS', name: 'Phòng Vận hành Tập đoàn', manager: 'Vũ Vận Hành' },
      ],
    },
    branches: [
      {
        branch_code: 'HN',
        branch_name: 'Chi nhánh Hà Nội',
        director: { full_name: 'Trần Giám Đốc HN', ma_nv: 'NV_HN_DIR_01' },
        departments: [
          { code: 'PB_HN_HR', name: 'Phòng Nhân sự HN', manager: 'Nguyễn Văn A' },
          { code: 'PB_HN_FIN', name: 'Phòng Tài vụ HN', manager: 'Trần Thị B' },
          { code: 'PB_HN_OPS', name: 'Phòng Vận hành HN', manager: 'Lê Văn C' },
          { code: 'PB_HN_KD', name: 'Phòng Kinh doanh HN', manager: 'Phạm Thị D' },
        ],
      },
      {
        branch_code: 'DN',
        branch_name: 'Chi nhánh Đà Nẵng',
        director: { full_name: 'Nguyễn Anh Tuấn', ma_nv: 'NV_DN_DIR_01' },
        departments: [
          { code: 'PB_DN_01', name: 'Phòng Kỹ thuật & R&D', manager: 'Vũ Đình Khang' },
          { code: 'PB_DN_HR', name: 'Phòng Nhân sự ĐN', manager: 'Hoàng Thị E' },
          { code: 'PB_DN_FIN', name: 'Phòng Tài vụ ĐN', manager: 'Đỗ Văn F' },
          { code: 'PB_DN_OPS', name: 'Phòng Vận hành ĐN', manager: 'Ngô Văn G' },
        ],
      },
      {
        branch_code: 'HCM',
        branch_name: 'Chi nhánh TP.HCM',
        director: { full_name: 'Huỳnh Quốc Bảo', ma_nv: 'NV_HCM_DIR_01' },
        departments: [
          { code: 'PB_HCM_01', name: 'Phòng Kinh doanh TP.HCM', manager: 'Trần Thị Mỹ Linh' },
          { code: 'PB_HCM_HR', name: 'Phòng Nhân sự HCM', manager: 'Lê Thị H' },
          { code: 'PB_HCM_FIN', name: 'Phòng Tài vụ HCM', manager: 'Vũ Văn I' },
          { code: 'PB_HCM_OPS', name: 'Phòng Vận hành HCM', manager: 'Trần Văn K' },
        ],
      },
    ],
  };

  const data = orgData || defaultOrgData;

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Spin size="large" tip="Đang tải sơ đồ cơ cấu tổ chức tập đoàn..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <Card bordered={false} className="shadow-xs border border-slate-200 rounded-xl">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-50 text-blue-600 rounded-xl text-2xl">
              <ApartmentOutlined />
            </div>
            <div>
              <Title level={4} className="!mb-0 text-slate-800">
                Sơ đồ Cơ cấu Tổ chức & Phân tách Đơn vị
              </Title>
              <Text className="text-slate-500 text-xs">
                Mô hình Tập đoàn: Phân biệt rõ Bộ máy Cấp Tập đoàn (Corporate HQ) và Bộ máy Chi nhánh Hà Nội (Branch HN) cùng 2 Chi nhánh ĐN & HCM
              </Text>
            </div>
          </div>
          <div className="flex gap-2">
            <Tag color="gold" className="px-3 py-1 font-semibold text-xs">
              ★ 1 BỘ MÁY TẬP ĐOÀN
            </Tag>
            <Tag color="blue" className="px-3 py-1 font-semibold text-xs">
              ● 3 CHI NHÁNH ĐỘC LẬP
            </Tag>
          </div>
        </div>
      </Card>

      {/* 1. CORPORATE HQ (TOP LEVEL) */}
      <Card
        bordered={false}
        className="shadow-sm border-2 border-amber-300 bg-gradient-to-r from-amber-50/50 via-white to-amber-50/30 rounded-xl overflow-hidden"
      >
        <div className="border-b border-amber-200 pb-3 mb-4 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <CrownOutlined className="text-xl text-amber-500" />
            <span className="font-bold text-base text-slate-800">
              {data.corporate_hq?.unit_name || 'Bộ Máy Điều Hành Cấp Tập Đoàn (Hà Nội)'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Tag color="gold" className="font-semibold">CẤP TẬP ĐOÀN (HQ)</Tag>
            <span className="text-xs text-slate-500">
              Lãnh đạo tối cao: <strong className="text-slate-800">{data.corporate_hq?.leader?.full_name}</strong> ({data.corporate_hq?.leader?.position})
            </span>
          </div>
        </div>

        <Row gutter={[16, 16]}>
          {data.corporate_hq?.departments?.map((dept) => (
            <Col xs={24} sm={12} lg={6} key={dept.code}>
              <div className="p-3 bg-white border border-amber-200 rounded-lg shadow-xs hover:border-amber-400 transition">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-mono font-bold text-amber-700">{dept.code}</span>
                  <Tag color="orange" className="text-[10px]">Tập đoàn</Tag>
                </div>
                <div className="font-semibold text-slate-800 text-sm">{dept.name}</div>
                <div className="text-xs text-slate-500 mt-2 flex items-center gap-1">
                  <UserOutlined className="text-slate-400" />
                  <span>Trưởng phòng: <strong>{dept.manager || 'Đang kiện toàn'}</strong></span>
                </div>
              </div>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 2. REGIONAL BRANCHES (3 SHARDS) */}
      <Title level={5} className="!text-slate-700 !mt-6">
        Các Đơn vị Chi nhánh Trực thuộc (Regional Branches)
      </Title>

      <Row gutter={[16, 16]}>
        {data.branches?.map((branch) => {
          const isHN = branch.branch_code === 'HN';
          return (
            <Col xs={24} lg={8} key={branch.branch_code}>
              <Card
                bordered={false}
                className={`shadow-xs border rounded-xl h-full ${
                  isHN ? 'border-blue-300 bg-blue-50/20' : 'border-slate-200 bg-white'
                }`}
              >
                <div className="border-b border-slate-100 pb-3 mb-3 flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <BankOutlined className={isHN ? 'text-blue-600' : 'text-slate-600'} />
                      <span className="font-bold text-slate-800">{branch.branch_name}</span>
                    </div>
                    <div className="text-xs text-slate-400 font-mono mt-0.5">
                      Mã Shard: {branch.branch_code} {isHN && '(Bộ máy Chi nhánh độc lập)'}
                    </div>
                  </div>
                  <Tag color={isHN ? 'blue' : branch.branch_code === 'DN' ? 'green' : 'purple'} className="font-semibold">
                    {branch.branch_code}
                  </Tag>
                </div>

                <div className="mb-4 p-2 bg-slate-50 rounded-lg text-xs flex items-center justify-between border border-slate-100">
                  <span className="text-slate-500">Giám đốc Chi nhánh:</span>
                  <span className="font-bold text-slate-800">{branch.director?.full_name}</span>
                </div>

                <div className="space-y-2">
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Các Phòng Ban Chức Năng:
                  </div>
                  {branch.departments?.map((dept) => (
                    <div
                      key={dept.code}
                      className="p-2.5 bg-white border border-slate-200 rounded-md shadow-xs flex justify-between items-center text-xs"
                    >
                      <div>
                        <div className="font-medium text-slate-800">{dept.name}</div>
                        <div className="text-[11px] text-slate-400 font-mono">{dept.code}</div>
                      </div>
                      <div className="text-right">
                        <span className="text-slate-400 text-[11px]">Trưởng phòng</span>
                        <div className="font-semibold text-slate-700">{dept.manager || '—'}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </Col>
          );
        })}
      </Row>
    </div>
  );
};

export default OrgChartPage;
