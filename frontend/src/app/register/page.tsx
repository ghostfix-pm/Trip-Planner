// src/app/register/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authService } from '@/services/auth';
import { Sparkles, Mail, Lock, User } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({ full_name: '', email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await authService.register(formData);
      // Đăng ký xong tự động đăng nhập luôn
      await authService.login(formData.email, formData.password);
      router.push('/');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="bg-white p-8 rounded-3xl shadow-xl border border-slate-100 w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <Sparkles className="w-10 h-10 text-indigo-600 mx-auto" />
          <h1 className="text-2xl font-bold text-slate-800">Tạo Tài Khoản</h1>
          <p className="text-slate-500 text-sm">Bắt đầu hành trình khám phá thế giới của bạn.</p>
        </div>

        {error && <div className="p-3 bg-red-50 text-red-600 text-sm rounded-xl text-center">{error}</div>}

        <form onSubmit={handleRegister} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Họ và tên</label>
            <div className="relative">
              <User className="w-5 h-5 absolute left-3 top-3 text-slate-400" />
              <input
                type="text"
                required
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:indigo-500 outline-none"
                placeholder="Nguyen Van A"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Email</label>
            <div className="relative">
              <Mail className="w-5 h-5 absolute left-3 top-3 text-slate-400" />
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:indigo-500 outline-none"
                placeholder="you@example.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Mật khẩu</label>
            <div className="relative">
              <Lock className="w-5 h-5 absolute left-3 top-3 text-slate-400" />
              <input
                type="password"
                required
                minLength={6}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:indigo-500 outline-none"
                placeholder="Ít nhất 6 ký tự"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 bg-indigo-600 text-white font-bold rounded-xl shadow-md hover:bg-indigo-700 transition disabled:opacity-50"
          >
            {loading ? 'Đang xử lý...' : 'Đăng Ký'}
          </button>
        </form>

        <p className="text-center text-sm text-slate-600">
          Đã có tài khoản?{' '}
          <Link href="/login" className="text-indigo-600 font-semibold hover:underline">
            Đăng nhập
          </Link>
        </p>
      </div>
    </main>
  );
}