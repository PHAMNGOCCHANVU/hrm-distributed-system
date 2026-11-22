import axiosClient from './axiosClient';

export const payrollApi = {
  getPayroll: (params) => axiosClient.get('/payroll', { params }),
  updatePayroll: (maNv, data) => axiosClient.put(`/payroll/${maNv}`, data),
  getMySlip: (params) => axiosClient.get('/payroll/my-slip', { params }),
};

export default payrollApi;
