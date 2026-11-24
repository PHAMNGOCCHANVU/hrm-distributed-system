import axiosClient from './axiosClient';

export const adminRequestApi = {
  getAdminRequests: (params) => axiosClient.get('/system-admin/requests', { params }),
  createAdminRequest: (data) => axiosClient.post('/system-admin/requests', data),
  approveAdminRequest: (id, decisionData) => axiosClient.put(`/system-admin/requests/${id}/approve`, decisionData),
  getClusterHealth: () => axiosClient.get('/system-admin/cluster-health'),
};

export default adminRequestApi;
