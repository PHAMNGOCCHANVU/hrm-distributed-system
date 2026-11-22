import axiosClient from './axiosClient';

export const systemApi = {
  getHealth: () => axiosClient.get('/system/health'),
  getAuditLogs: (params) => axiosClient.get('/system/audit-logs', { params }),
};

export default systemApi;
