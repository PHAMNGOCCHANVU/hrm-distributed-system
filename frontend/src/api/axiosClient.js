import axios from 'axios';
import { message } from 'antd';

const axiosClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach Bearer token from localStorage
axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401, 403, network errors
axiosClient.interceptors.response.use(
  (response) => {
    // Return the response data directly
    return response.data;
  },
  (error) => {
    const { response } = error;
    if (response) {
      const { status, data } = response;
      const errorMsg = data?.error?.message || data?.message || 'Đã có lỗi xảy ra';

      if (status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
        message.error('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      } else if (status === 403) {
        message.error(errorMsg || 'Bạn không có quyền thực hiện thao tác này!');
      } else if (status === 400) {
        message.error(errorMsg || 'Yêu cầu không hợp lệ.');
      } else if (status === 500) {
        message.error(errorMsg || 'Lỗi máy chủ nội bộ. Vui lòng thử lại sau.');
      } else {
        message.error(errorMsg);
      }
    } else {
      message.error('Không thể kết nối đến máy chủ. Vui lòng kiểm tra mạng hoặc trạng thái backend.');
    }
    return Promise.reject(error);
  }
);

export default axiosClient;
