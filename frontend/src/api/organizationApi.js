import axiosClient from './axiosClient';

export const organizationApi = {
  getOrgTree: () => axiosClient.get('/organizations/tree'),
  getDepartments: (params) => axiosClient.get('/organizations/departments', { params }),
};

export default organizationApi;
