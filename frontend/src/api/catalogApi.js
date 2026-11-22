import axiosClient from './axiosClient';

export const catalogApi = {
  getDepartments: () => axiosClient.get('/catalogs/departments'),
  getPositions: () => axiosClient.get('/catalogs/positions'),
  getRoles: () => axiosClient.get('/catalogs/roles'),
  getProjects: () => axiosClient.get('/catalogs/projects'),
  createProject: (data) => axiosClient.post('/catalogs/projects', data),
};

export default catalogApi;
