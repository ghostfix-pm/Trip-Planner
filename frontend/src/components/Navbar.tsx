// src/components/Navbar.tsx
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { authService } from '@/services/auth';
import { Compass, User, LogOut, History } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Kiểm tra trạng thái đăng nhập khi component được render
  useEffect(() => {
    const token = authService.getToken();
    setIsLoggedIn(!!token);
  }, [pathname]); // Cập nhật lại mỗi khi chuyển trang

  const handleLogout = () => {
    authService.logout();
    setIsLoggedIn(false);
  };

  return (
    <nav className="sticky top-0 z-50 w-full bg-white/80 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        
        {/* Logo & Tên App */}
        <Link href="/" className="flex items-center gap-2 text-blue-600 hover:opacity-80 transition">
          <Compass className="w-6 h-6" />
          <span className="font-bold text-lg tracking-tight">TripPlanner AI</span>
        </Link>

        {/* Menu Bên Phải */}
        <div className="flex items-center gap-3">
          {isLoggedIn ? (
            <>
              <Link 
                href="/trips" 
                className="hidden sm:flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100 transition"
              >
                <History className="w-4 h-4" />
                Chuyến đi của tôi
              </Link>
              <button 
                onClick={handleLogout}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-red-600 hover:bg-red-50 transition"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Đăng xuất</span>
              </button>
            </>
          ) : (
            <>
              <Link 
                href="/login" 
                className="px-4 py-2 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100 transition"
              >
                Đăng nhập
              </Link>
              <Link 
                href="/register" 
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-bold bg-blue-600 text-white hover:bg-blue-700 shadow-md transition"
              >
                <User className="w-4 h-4" />
                Đăng ký
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}