import axiosClient from './axiosClient';

export const appointmentApi = {
  getAppointments: (params) => axiosClient.get('/appointments', { params }),
  createAppointment: (data) => axiosClient.post('/appointments', data),
  approveAppointment: (id, decisionData) => axiosClient.put(`/appointments/${id}/approve`, decisionData),
};

export default appointmentApi;
