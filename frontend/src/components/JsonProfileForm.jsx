import React from 'react';
import { Form, Input, Select, Button, Space, Card, Typography, Divider } from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';

const { Text } = Typography;
const { Option } = Select;

export const JsonProfileForm = () => {
  return (
    <div className="space-y-6">
      {/* Dynamic JSON Skills */}
      <Card
        size="small"
        title={<span className="font-semibold text-slate-700">Danh mục kỹ năng chuyên môn (JSONB `skills`)</span>}
        className="bg-slate-50/50"
      >
        <Form.List name="skills">
          {(fields, { add, remove }) => (
            <>
              {fields.map(({ key, name, ...restField }) => (
                <Space
                  key={key}
                  style={{ display: 'flex', marginBottom: 8 }}
                  align="baseline"
                  className="w-full flex items-center gap-2"
                >
                  <Form.Item
                    {...restField}
                    name={[name, 'name']}
                    rules={[{ required: true, message: 'Nhập tên kỹ năng' }]}
                    className="mb-0 flex-1"
                  >
                    <Input placeholder="Tên kỹ năng (VD: React, Docker, Python)" />
                  </Form.Item>
                  <Form.Item
                    {...restField}
                    name={[name, 'level']}
                    rules={[{ required: true, message: 'Chọn cấp độ' }]}
                    className="mb-0 w-36"
                  >
                    <Select placeholder="Cấp độ">
                      <Option value="Beginner">Beginner</Option>
                      <Option value="Intermediate">Intermediate</Option>
                      <Option value="Advanced">Advanced</Option>
                      <Option value="Expert">Expert</Option>
                    </Select>
                  </Form.Item>
                  <MinusCircleOutlined
                    className="text-rose-500 hover:text-rose-700 cursor-pointer"
                    onClick={() => remove(name)}
                  />
                </Space>
              ))}
              <Form.Item className="mb-0 mt-3">
                <Button
                  type="dashed"
                  onClick={() => add()}
                  block
                  icon={<PlusOutlined />}
                  className="border-slate-300 text-slate-600 hover:text-blue-600"
                >
                  Thêm kỹ năng chuyên môn
                </Button>
              </Form.Item>
            </>
          )}
        </Form.List>
      </Card>

      {/* Dynamic JSON Performance Reviews */}
      <Card
        size="small"
        title={<span className="font-semibold text-slate-700">Đánh giá hiệu suất KPI (JSONB `performance_reviews`)</span>}
        className="bg-slate-50/50"
      >
        <Form.List name="performance_reviews">
          {(fields, { add, remove }) => (
            <>
              {fields.map(({ key, name, ...restField }) => (
                <div key={key} className="p-3 mb-3 bg-white border border-slate-200 rounded-md relative">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-2">
                    <Form.Item
                      {...restField}
                      label="Kỳ đánh giá"
                      name={[name, 'period']}
                      rules={[{ required: true, message: 'Nhập kỳ' }]}
                      className="mb-0"
                    >
                      <Input placeholder="VD: 2026-Q1" />
                    </Form.Item>
                    <Form.Item
                      {...restField}
                      label="Xếp loại KPI"
                      name={[name, 'final_grade']}
                      rules={[{ required: true, message: 'Chọn xếp loại' }]}
                      className="mb-0"
                    >
                      <Select placeholder="Chọn xếp loại">
                        <Option value="A">Hạng A (Xuất sắc)</Option>
                        <Option value="B">Hạng B (Hoàn thành tốt)</Option>
                        <Option value="C">Hạng C (Cần cải thiện)</Option>
                      </Select>
                    </Form.Item>
                    <div className="flex items-center justify-end">
                      <Button
                        type="text"
                        danger
                        size="small"
                        icon={<MinusCircleOutlined />}
                        onClick={() => remove(name)}
                      >
                        Xóa kỳ này
                      </Button>
                    </div>
                  </div>
                  <Form.Item
                    {...restField}
                    label="Nhận xét / Đánh giá chi tiết"
                    name={[name, 'feedback']}
                    rules={[{ required: true, message: 'Nhập nhận xét' }]}
                    className="mb-0"
                  >
                    <Input.TextArea rows={2} placeholder="Nhận xét tiến độ hoàn thành công việc và thái độ..." />
                  </Form.Item>
                </div>
              ))}
              <Form.Item className="mb-0 mt-2">
                <Button
                  type="dashed"
                  onClick={() => add()}
                  block
                  icon={<PlusOutlined />}
                  className="border-slate-300 text-slate-600 hover:text-blue-600"
                >
                  Thêm bản đánh giá KPI
                </Button>
              </Form.Item>
            </>
          )}
        </Form.List>
      </Card>
    </div>
  );
};

export default JsonProfileForm;
