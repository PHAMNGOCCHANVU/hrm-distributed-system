import axiosClient from './axiosClient';

export const reportApi = {
  getHeadcountReport: (params) => axiosClient.get('/reports/headcount', { params }),
};

export default reportApi;
