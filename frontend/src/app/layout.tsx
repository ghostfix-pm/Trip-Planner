// src/app/layout.tsx
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar"; // <-- Import Navbar

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TripPlanner AI - Lên Kế Hoạch Du Lịch",
  description: "Hệ thống tự động lọc nhiễu, phân tích ý định và tìm kiếm tổ hợp du lịch tối ưu.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-slate-50">
        <Navbar /> {/* <-- Đặt Navbar ở ngay đầu body */}
        <div className="flex-1">
          {children}
        </div>
      </body>
    </html>
  );
}