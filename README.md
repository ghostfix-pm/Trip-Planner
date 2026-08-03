# 🗺️ Trip Planner - Ứng Dụng Quản Lý & Lập Kế Hoạch Du Lịch

<!-- BADGES -->
![React](https://img.shields.io/badge/Frontend-React.js-61DAFB?style=for-the-badge&logo=react)
![NodeJS](https://img.shields.io/badge/Backend-Node.js-339933?style=for-the-badge&logo=nodedotjs)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248?style=for-the-badge&logo=mongodb)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **Trip Planner** là ứng dụng hỗ trợ người dùng dễ dàng lên lịch trình du lịch chi tiết, tối ưu hóa tuyến đường di chuyển, theo dõi ngân sách và chia sẻ chuyến đi cùng bạn bè.

🔗 **Live Demo:** [https://trip-planner.demo.app](https://trip-planner.demo.app)  
📑 **API Documentation:** [https://api.trip-planner.demo.app/docs](https://api.trip-planner.demo.app/docs)

---

## 📸 Demo & Giao Diện (Screenshots / GIF)

| Lịch trình du lịch | Quản lý ngân sách & Bản đồ |
| :---: | :---: |
| ![Itinerary Demo](https://via.placeholder.com/400x250?text=Itinerary+View) | ![Map & Budget Demo](https://via.placeholder.com/400x250?text=Map+%26+Budget) |

---

## 📌 Tổng Quan Dự Án & Bài Toán Giải Quyết

Khi lên kế hoạch đi du lịch, người dùng thường gặp khó khăn trong việc tổng hợp các địa điểm tham quan, theo dõi chi tiêu thực tế so với dự kiến, và tối ưu tuyến đường di chuyển giữa các điểm.

**Trip Planner** giải quyết các bài toán này thông qua:
- Sắp xếp và quản lý lịch trình theo mốc thời gian trực quan.
- Tự động hóa tính toán chi phí và phân chia ngân sách nhóm.
- Tích hợp bản đồ trực quan giúp định vị và gợi ý lộ trình ngắn nhất.

---

## ✨ Tính Năng Chính

- 📅 **Lập Lịch Trình Chi Tiết:** Tạo chuyến đi, thêm/sửa/xóa điểm đến, sắp xếp thứ tự tham quan kéo thả (Drag & Drop).
- 💰 **Quản Lý Chi Phí:** Ghi chép chi tiêu, tự động tính tổng ngân sách và chia tiền giữa các thành viên.
- 🗺️ **Tích Hợp Bản Đồ:** Hiển thị vị trí các điểm tham quan trên Google Maps API / Leaflet.
- 👥 **Cộng Tác Real-time:** Mời bạn bè cùng chỉnh sửa lịch trình theo thời gian thực (Socket.io).
- 📱 **Responsive Design:** Tối ưu hóa trải nghiệm mượt mà trên cả Mobile và Desktop.

---

## 🛠️ Công Nghệ Sử Dụng (Tech Stack)

### Frontend
- **Framework:** React.js (Vite) / Next.js
- **State Management:** Redux Toolkit / Zustand
- **UI & Styling:** Tailwind CSS, Ant Design / Shadcn UI
- **Maps:** Google Maps JavaScript API / Mapbox

### Backend
- **Runtime & Framework:** Node.js (Express.js) / Python (Django/FastAPI)
- **Database:** MongoDB (Mongoose) / PostgreSQL (Prisma ORM)
- **Authentication:** JWT, OAuth 2.0 (Google Login)

### DevOps & Tools
- **Deployment:** Vercel (Frontend), Render / AWS EC2 (Backend)
- **CI/CD:** GitHub Actions (Automated Test & Build)

---

## 🏗️ Kiến Trúc Hệ Thống (Architecture)

```text
[Client: React.js] ──(HTTPS / RESTful API)──> [Server: Express.js]
                                                   │
                                                   ├──> [Database: MongoDB]
                                                   └──> [External APIs: Google Maps, OpenWeather]
