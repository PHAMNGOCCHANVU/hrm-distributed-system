import axiosClient from './axiosClient';

export const employeeApi = {
  getAll: (params) => axiosClient.get('/employees', { params }),
  getById: (maNv) => axiosClient.get(`/employees/${maNv}`),
  create: (formData) =>
    axiosClient.post('/employees', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  update: (maNv, formData) =>
    axiosClient.put(`/employees/${maNv}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  delete: (maNv) => axiosClient.delete(`/employees/${maNv}`),
  getColleagues: () => axiosClient.get('/employees/colleagues'),
};

export default employeeApi;
