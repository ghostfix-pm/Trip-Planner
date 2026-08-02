// src/services/auth.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

export const authService = {
  // 1. Đăng ký
  async register(data: any) {
    const res = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Đăng ký thất bại');
    }
    return res.json();
  },

  // 2. Đăng nhập (Dùng x-www-form-urlencoded chuẩn OAuth2 của FastAPI)
  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email); // FastAPI OAuth2 mặc định dùng 'username'
    formData.append('password', password);

    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });
    
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Sai tài khoản hoặc mật khẩu');
    }
    
    const data = await res.json();
    // Lưu Token vào LocalStorage
    localStorage.setItem('access_token', data.access_token);
    return data;
  },

  // 3. Đăng xuất
  logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  },

  // 4. Lấy Token hiện tại
  getToken() {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  }
};