// src/components/TripForm.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { tripApi } from '@/services/api'; // Hãy đảm bảo API URL được config đúng
import { Plane, MapPin, Sparkles, Calendar, Users, DollarSign, Hotel, Utensils, Activity, Settings2 } from 'lucide-react';

// Định nghĩa Interface tạm thời cho Form (Bạn có thể chuyển nó vào api.ts sau)
interface TripRequest {
  origin: string;
  destination: string;
  departure_date: string;
  return_date: string;
  min_budget: number;
  max_budget: number;
  num_adults: number;
  num_children: number;
  num_infants: number;
  num_elderly: number;
  hotel_price_level: string;
  hotel_amenities: string[];
  hotel_categories: string[];
  food_price_level: string;
  food_categories: string[];
  activity_categories: string[];
  flight_class: string;
  non_stop_only: boolean;
  travel_pace: string;
}

export default function TripForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [tagsConfig, setTagsConfig] = useState<any>(null);

  // Khởi tạo giá trị mặc định cho form
  const [formData, setFormData] = useState<TripRequest>({
    origin: 'Hà Nội',
    destination: 'Hồ Chí Minh',
    departure_date: new Date().toISOString().split('T')[0], // Hôm nay
    return_date: new Date(Date.now() + 3 * 86400000).toISOString().split('T')[0], // 3 ngày sau
    min_budget: 2000,
    max_budget: 5000,
    num_adults: 1,
    num_children: 0,
    num_infants: 0,
    num_elderly: 0,
    hotel_price_level: 'moderate',
    hotel_amenities: [],
    hotel_categories: [],
    food_price_level: 'standard',
    food_categories: [],
    activity_categories: [],
    flight_class: 'economy',
    non_stop_only: false,
    travel_pace: 'balanced'
  });

  // Gọi API lấy tag_config từ backend
  useEffect(() => {
    const fetchTags = async () => {
      try {
        const data = await tripApi.getTagsConfig();
        setTagsConfig(data);
      } catch (error) {
        console.error("Lỗi:", error);
      }
    };
    fetchTags();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const result = await tripApi.planTrip(formData as any);
      if (result.tripId) {
        router.push(`/itinerary/${result.tripId}`);
      }
    } catch (error) {
      console.error("Lỗi gọi API lập kế hoạch:", error);
      alert("Đã có lỗi xảy ra. Vui lòng kiểm tra lại cấu hình hoặc đăng nhập.");
    } finally {
      setLoading(false);
    }
  };

  // Hàm xử lý việc Check/Uncheck cho các mảng (List[str])
  const toggleArrayItem = (field: keyof TripRequest, value: string) => {
    setFormData((prev: any) => {
      const array = prev[field] as string[];
      if (array.includes(value)) {
        return { ...prev, [field]: array.filter((item) => item !== value) };
      } else {
        return { ...prev, [field]: [...array, value] };
      }
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-8 rounded-3xl shadow-xl border border-slate-100 max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold text-slate-800 flex items-center justify-center gap-2">
          <Sparkles className="w-8 h-8 text-blue-600" />
          Lên Kế Hoạch Đa Phương Tiện
        </h2>
        <p className="text-slate-500">Tùy chỉnh sâu từng thông số chuyến đi của bạn</p>
      </div>

      {/* BLOCK 1: HÀNH TRÌNH CƠ BẢN */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold border-b pb-2 flex items-center gap-2 text-slate-700">
          <Plane className="w-5 h-5 text-blue-500" /> Hành Trình & Chuyến Bay
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Điểm xuất phát (Mã IATA/Tên)</label>
            <input type="text" required value={formData.origin} onChange={(e) => setFormData({...formData, origin: e.target.value})} className="w-full p-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Điểm đến (Mã IATA/Tên)</label>
            <input type="text" required value={formData.destination} onChange={(e) => setFormData({...formData, destination: e.target.value})} className="w-full p-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Ngày đi</label>
            <input type="date" required value={formData.departure_date} onChange={(e) => setFormData({...formData, departure_date: e.target.value})} className="w-full p-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Ngày về</label>
            <input type="date" required value={formData.return_date} onChange={(e) => setFormData({...formData, return_date: e.target.value})} className="w-full p-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
          <div>
             <label className="block text-sm font-semibold text-slate-700 mb-1">Hạng vé máy bay</label>
             <select value={formData.flight_class} onChange={(e) => setFormData({...formData, flight_class: e.target.value})} className="w-full p-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none">
                <option value="economy">Economy</option>
                <option value="premium_economy">Premium Economy</option>
                <option value="business">Business</option>
                <option value="first">First Class</option>
             </select>
          </div>
          <div className="flex items-center mt-6">
            <label className="flex items-center gap-2 cursor-pointer font-semibold text-sm text-slate-700">
              <input type="checkbox" checked={formData.non_stop_only} onChange={(e) => setFormData({...formData, non_stop_only: e.target.checked})} className="w-5 h-5 rounded text-blue-600 focus:ring-blue-500" />
              Chỉ tìm chuyến bay thẳng (Non-stop)
            </label>
          </div>
        </div>
      </div>

      {/* BLOCK 2: HÀNH KHÁCH & NGÂN SÁCH */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold border-b pb-2 flex items-center gap-2 text-slate-700">
          <Users className="w-5 h-5 text-emerald-500" /> Đoàn Khách & Ngân Sách
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Người lớn</label>
            <input type="number" min="1" value={formData.num_adults} onChange={(e) => setFormData({...formData, num_adults: Number(e.target.value)})} className="w-full p-2.5 rounded-xl border border-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Trẻ em</label>
            <input type="number" min="0" value={formData.num_children} onChange={(e) => setFormData({...formData, num_children: Number(e.target.value)})} className="w-full p-2.5 rounded-xl border border-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Em bé</label>
            <input type="number" min="0" value={formData.num_infants} onChange={(e) => setFormData({...formData, num_infants: Number(e.target.value)})} className="w-full p-2.5 rounded-xl border border-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Người già</label>
            <input type="number" min="0" value={formData.num_elderly} onChange={(e) => setFormData({...formData, num_elderly: Number(e.target.value)})} className="w-full p-2.5 rounded-xl border border-slate-200" />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Ngân sách TỐI THIỂU (USD)</label>
            <input type="number" min="0" value={formData.min_budget} onChange={(e) => setFormData({...formData, min_budget: Number(e.target.value)})} className="w-full p-2.5 rounded-xl border border-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Ngân sách TỐI ĐA (USD)</label>
            <input type="number" min="1" value={formData.max_budget} onChange={(e) => setFormData({...formData, max_budget: Number(e.target.value)})} className="w-full p-2.5 rounded-xl border border-slate-200" />
          </div>
        </div>
      </div>

      {/* BLOCK 3: KHÁCH SẠN */}
      <div className="space-y-4 bg-slate-50 p-5 rounded-2xl border border-slate-100">
        <h3 className="text-lg font-bold border-b border-slate-200 pb-2 flex items-center gap-2 text-slate-700">
          <Hotel className="w-5 h-5 text-amber-500" /> Yêu cầu Khách sạn
        </h3>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">Mức giá</label>
          <select value={formData.hotel_price_level} onChange={(e) => setFormData({...formData, hotel_price_level: e.target.value})} className="w-full md:w-1/2 p-2.5 rounded-xl border border-slate-200">
            <option value="budget">Tiết kiệm (Budget)</option>
            <option value="moderate">Vừa phải (Moderate)</option>
            <option value="upscale">Cao cấp (Upscale)</option>
            <option value="luxury">Sang trọng (Luxury)</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">Loại hình lưu trú</label>
          <div className="flex flex-wrap gap-2">
            {(tagsConfig?.hotel_categories || ['Resort', 'Homestay', 'Villa', 'Hostel', 'Apartment']).map((tag: string) => (
              <button type="button" key={tag} onClick={() => toggleArrayItem('hotel_categories', tag)} 
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition ${formData.hotel_categories.includes(tag) ? 'bg-amber-100 border-amber-300 text-amber-800' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100'}`}>
                {tag}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">Tiện ích bắt buộc</label>
          <div className="flex flex-wrap gap-2">
            {(tagsConfig?.hotel_amenities || ['Pool', 'WiFi', 'Breakfast Included', 'Gym', 'Parking', 'Spa']).map((tag: string) => (
              <button type="button" key={tag} onClick={() => toggleArrayItem('hotel_amenities', tag)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition ${formData.hotel_amenities.includes(tag) ? 'bg-blue-100 border-blue-300 text-blue-800' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100'}`}>
                {tag}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* BLOCK 4: ẨM THỰC & VUI CHƠI */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold border-b pb-2 flex items-center gap-2 text-slate-700">
          <Activity className="w-5 h-5 text-rose-500" /> Trải Nghiệm & Ẩm Thực
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
           <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Mức giá ăn uống</label>
            <select value={formData.food_price_level} onChange={(e) => setFormData({...formData, food_price_level: e.target.value})} className="w-full p-2.5 rounded-xl border border-slate-200">
              <option value="budget">Bình dân</option>
              <option value="standard">Tiêu chuẩn</option>
              <option value="gourmet">Nhà hàng cao cấp</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Nhịp độ di chuyển (Travel Pace)</label>
            <select value={formData.travel_pace} onChange={(e) => setFormData({...formData, travel_pace: e.target.value})} className="w-full p-2.5 rounded-xl border border-slate-200">
              <option value="relaxed">Thư giãn (Ít điểm/ngày)</option>
              <option value="balanced">Cân bằng</option>
              <option value="packed">Dày đặc (Nhiều điểm/ngày)</option>
            </select>
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">Sở thích ẩm thực</label>
          <div className="flex flex-wrap gap-2">
            {(tagsConfig?.food_categories || ['Seafood', 'Street Food', 'Vegan', 'Local Cuisine', 'BBQ', 'Cafe']).map((tag: string) => (
              <button type="button" key={tag} onClick={() => toggleArrayItem('food_categories', tag)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition ${formData.food_categories.includes(tag) ? 'bg-rose-100 border-rose-300 text-rose-800' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100'}`}>
                {tag}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">Hoạt động giải trí</label>
          <div className="flex flex-wrap gap-2">
            {(tagsConfig?.activity_categories || ['Museum', 'Nature', 'Theme Park', 'Nightlife', 'Shopping', 'Historical']).map((tag: string) => (
              <button type="button" key={tag} onClick={() => toggleArrayItem('activity_categories', tag)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition ${formData.activity_categories.includes(tag) ? 'bg-indigo-100 border-indigo-300 text-indigo-800' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100'}`}>
                {tag}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Nút Submit */}
      <button
        type="submit"
        disabled={loading}
        className="w-full py-4 bg-linear-to-r from-blue-600 to-indigo-600 text-white font-bold rounded-2xl shadow-lg hover:opacity-90 transition disabled:opacity-50 flex items-center justify-center gap-2 mt-8"
      >
        {loading ? (
          <><div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> Đang tối ưu hóa hành trình...</>
        ) : (
          <><Settings2 className="w-5 h-5" /> Khởi tạo lịch trình AI</>
        )}
      </button>
    </form>
  );
}