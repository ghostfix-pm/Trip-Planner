// src/app/page.tsx
"use client";

import { FormEvent, useState, useEffect } from "react";
import MarkdownView from "@/components/MarkdownView";
import LocationAutocomplete from "@/components/LocationAutocomplete";
import PlaceDetailCard from "@/components/PlaceDetailCard";
import HotelDetailSection from "@/components/HotelDetailSection";
import { tripApi, TripRequest, TravelPlannerResponse, ItineraryOption } from "@/services/api";
import { Sparkles, Hotel, Utensils, Compass, ExternalLink, Wifi, Car, Plane, Users, Activity, Settings2, MapPin } from "lucide-react";

const getFutureDate = (daysToAdd: number) => {
  const date = new Date();
  date.setDate(date.getDate() + daysToAdd);
  return date.toISOString().split('T')[0];
};

const initialForm: TripRequest = {
  origin: "Hà Nội, Vietnam",
  destination: "Đà Nẵng, Vietnam",
  departure_date: getFutureDate(1),
  return_date: getFutureDate(4),
  min_budget: 2000,
  max_budget: 5000,
  num_adults: 2,
  num_children: 0,
  num_infants: 0,
  num_elderly: 0,
  hotel_price_level: "moderate",
  hotel_amenities: [],
  food_price_level: "standard",
  food_categories: [],
  activity_categories: [],
  flight_class: "economy",
  non_stop_only: false,
  travel_pace: "balanced",
};

export default function Home() {
  const [form, setForm] = useState<TripRequest>(initialForm);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<TravelPlannerResponse | null>(null);
  const [selectedOptionIndex, setSelectedOptionIndex] = useState<number>(0);
  const [activeTab, setActiveTab] = useState<'itinerary' | 'candidates'>('itinerary');
  const [tagsConfig, setTagsConfig] = useState<any>(null);

  useEffect(() => {
    const fetchTags = async () => {
      try {
        const data = await tripApi.getTagsConfig();
        setTagsConfig(data);
      } catch (error) {
        console.error("Lỗi lấy cấu hình tag:", error);
      }
    };
    fetchTags();
  }, []);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setResponse(null);

    try {
      const res = await tripApi.planTrip(form);
      setResponse(res);
      setSelectedOptionIndex(0);
    } catch (error) {
      alert(error instanceof Error ? error.message : "Đã có lỗi xảy ra");
    } finally {
      setLoading(false);
    }
  };

  const toggleArrayItem = (field: keyof TripRequest, value: string) => {
    setForm((prev: any) => {
      const array = prev[field] as string[];
      if (array.includes(value)) {
        return { ...prev, [field]: array.filter((item) => item !== value) };
      } else {
        return { ...prev, [field]: [...array, value] };
      }
    });
  };

  const itineraryOptions: ItineraryOption[] = response?.itinerary_options?.length
    ? response.itinerary_options
    : [];
  const selectedOption: ItineraryOption | null = itineraryOptions[selectedOptionIndex] || null;
  const primaryOption: ItineraryOption | null = response?.itinerary_options?.[0] || selectedOption;

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-10 text-slate-900 font-sans">
      <div className="mx-auto flex max-w-350 flex-col gap-8">
        
        {/* HEADER */}
        <header className="text-center space-y-3">
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">Multi-Agent Planner</p>
          <h1 className="text-4xl md:text-5xl font-black tracking-tight text-slate-800">Tạo Lịch Trình Thông Minh</h1>
          <p className="text-slate-600 max-w-2xl mx-auto font-medium">
            Hệ thống tự động lọc nhiễu, phân tích ý định và tìm kiếm tổ hợp tối ưu chi phí.
          </p>
        </header>

        {/* PHẦN CHIA CỘT TRÁI - PHẢI CỦA FORM VÀ KẾT QUẢ TEXT */}
        <div className="grid gap-8 lg:grid-cols-[450px_1fr] items-start">
          
          {/* CỘT TRÁI: FORM REQUEST */}
          <form onSubmit={handleSubmit} className="space-y-6 rounded-3xl border border-slate-200 bg-white px-6 shadow-sm h-fit max-h-[85vh] overflow-y-auto custom-scrollbar relative top-6">
            <h2 className="text-lg font-extrabold text-slate-800 flex items-center gap-2 border-b pb-4 pt-6 sticky top-0 bg-white z-20">
              <Sparkles className="w-5 h-5 text-blue-600" />
              Thông Tin Chuyến Đi
            </h2>

            {/* Khối 1: Hành trình */}
            <div className="space-y-3">
              <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5 uppercase tracking-wide">
                <Plane className="w-4 h-4 text-blue-500" /> Hành Trình
              </span>
              <div className="grid gap-3 sm:grid-cols-2">
                <label className="space-y-1 text-xs font-semibold">
                  <span>Từ (IATA/Tên)</span>
                  <LocationAutocomplete 
                    placeholder="Tìm thành phố..." 
                    value={form.origin} 
                    onChange={(val) => setForm({ ...form, origin: val })} 
                    cities={tagsConfig?.CITIES_DB || tagsConfig?.cities || []} 
                  />
                </label>
                <label className="space-y-1 text-xs font-semibold">
                  <span>Đến (IATA/Tên)</span>
                  <LocationAutocomplete 
                    placeholder="Tìm thành phố..." 
                    value={form.destination} 
                    onChange={(val) => setForm({ ...form, destination: val })} 
                    cities={tagsConfig?.CITIES_DB || tagsConfig?.cities || []} 
                  />
                </label>
                <label className="space-y-1 text-xs font-semibold">
                  <span>Ngày đi</span>
                  <input type="date" className="w-full rounded-xl border border-slate-300 px-3 py-2 bg-slate-50 focus:bg-white transition outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500" required value={form.departure_date} onChange={(e) => setForm({ ...form, departure_date: e.target.value })} />
                </label>
                <label className="space-y-1 text-xs font-semibold">
                  <span>Ngày về</span>
                  <input type="date" className="w-full rounded-xl border border-slate-300 px-3 py-2 bg-slate-50 focus:bg-white transition outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500" required value={form.return_date} onChange={(e) => setForm({ ...form, return_date: e.target.value })} />
                </label>
              </div>
            </div>

            {/* Khối 2: Khách & Ngân sách */}
            <div className="space-y-3 border-t pt-4">
              <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5 uppercase tracking-wide">
                <Users className="w-4 h-4 text-emerald-500" /> Đoàn khách & Ngân sách
              </span>
              <div className="grid gap-3 grid-cols-4">
                <label className="space-y-1 text-[10px] font-semibold text-center">
                  <span>Người lớn</span>
                  <input type="number" min="1" className="w-full rounded-lg border border-slate-300 px-2 py-1.5 text-center bg-slate-50" value={form.num_adults} onChange={(e) => setForm({ ...form, num_adults: Number(e.target.value) })} />
                </label>
                <label className="space-y-1 text-[10px] font-semibold text-center">
                  <span>Trẻ em</span>
                  <input type="number" min="0" className="w-full rounded-lg border border-slate-300 px-2 py-1.5 text-center bg-slate-50" value={form.num_children} onChange={(e) => setForm({ ...form, num_children: Number(e.target.value) })} />
                </label>
                <label className="space-y-1 text-[10px] font-semibold text-center">
                  <span>Em bé</span>
                  <input type="number" min="0" className="w-full rounded-lg border border-slate-300 px-2 py-1.5 text-center bg-slate-50" value={form.num_infants} onChange={(e) => setForm({ ...form, num_infants: Number(e.target.value) })} />
                </label>
                <label className="space-y-1 text-[10px] font-semibold text-center">
                  <span>Người già</span>
                  <input type="number" min="0" className="w-full rounded-lg border border-slate-300 px-2 py-1.5 text-center bg-slate-50" value={form.num_elderly} onChange={(e) => setForm({ ...form, num_elderly: Number(e.target.value) })} />
                </label>
              </div>
              <div className="grid gap-3 sm:grid-cols-2 mt-2">
                <label className="space-y-1 text-xs font-semibold">
                  <span>Ngân sách Min ($)</span>
                  <input type="number" step="500" className="w-full rounded-xl border border-slate-300 px-3 py-2 bg-slate-50" value={form.min_budget} onChange={(e) => setForm({ ...form, min_budget: Number(e.target.value) })} />
                </label>
                <label className="space-y-1 text-xs font-semibold">
                  <span>Ngân sách Max ($)</span>
                  <input type="number" step="500" required className="w-full rounded-xl border border-slate-300 px-3 py-2 bg-slate-50" value={form.max_budget} onChange={(e) => setForm({ ...form, max_budget: Number(e.target.value) })} />
                </label>
              </div>
            </div>

            {/* Khối 3: Khách sạn */}
            <div className="space-y-3 border-t pt-4">
              <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5 uppercase tracking-wide">
                <Hotel className="w-4 h-4 text-amber-500" /> Tiêu chuẩn Khách sạn
              </span>
              <select value={form.hotel_price_level} onChange={(e) => setForm({ ...form, hotel_price_level: e.target.value })} className="w-full rounded-xl border border-slate-300 p-2.5 text-xs bg-slate-50">
                <option value="budget">Tiết kiệm (Budget)</option>
                <option value="moderate">Vừa phải (Moderate)</option>
                <option value="upscale">Cao cấp (Upscale)</option>
                <option value="luxury">Sang trọng (Luxury)</option>
              </select>
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Tiện ích (Chọn nhiều)</span>
                <div className="flex flex-wrap gap-1.5">
                  {(tagsConfig?.hotel_amenities || ['pool', 'wifi', 'breakfast', 'gym']).map((tag: string) => (
                    <button type="button" key={tag} onClick={() => toggleArrayItem('hotel_amenities', tag)} className={`px-2 py-1 text-[10px] font-semibold rounded-md border transition ${form.hotel_amenities.includes(tag) ? 'bg-blue-100 border-blue-300 text-blue-800 shadow-sm' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'}`}>
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Khối 4: Trải nghiệm & Ăn uống */}
            <div className="space-y-3 border-t pt-4">
              <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5 uppercase tracking-wide">
                <Activity className="w-4 h-4 text-rose-500" /> Trải nghiệm & Ăn uống
              </span>
              <div className="grid gap-3 sm:grid-cols-2">
                <select value={form.food_price_level} onChange={(e) => setForm({ ...form, food_price_level: e.target.value })} className="w-full rounded-xl border border-slate-300 p-2.5 text-xs bg-slate-50">
                  <option value="budget">Ăn uống: Bình dân</option>
                  <option value="standard">Ăn uống: Tiêu chuẩn</option>
                  <option value="gourmet">Ăn uống: Cao cấp</option>
                </select>
                <select value={form.travel_pace} onChange={(e) => setForm({ ...form, travel_pace: e.target.value })} className="w-full rounded-xl border border-slate-300 p-2.5 text-xs bg-slate-50">
                  <option value="relaxed">Nhịp độ: Thư giãn</option>
                  <option value="balanced">Nhịp độ: Cân bằng</option>
                  <option value="packed">Nhịp độ: Dày đặc</option>
                </select>
              </div>
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Ẩm thực</span>
                <div className="flex flex-wrap gap-1.5">
                  {(tagsConfig?.food_categories || ['seafood', 'bbq', 'cafe', 'local']).map((tag: string) => (
                    <button type="button" key={tag} onClick={() => toggleArrayItem('food_categories', tag)} className={`px-2 py-1 text-[10px] font-semibold rounded-md border transition ${form.food_categories.includes(tag) ? 'bg-rose-100 border-rose-300 text-rose-800 shadow-sm' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'}`}>
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Giải trí</span>
                <div className="flex flex-wrap gap-1.5">
                  {(tagsConfig?.activity_categories || ['landmark', 'beach', 'museum', 'shopping']).map((tag: string) => (
                    <button type="button" key={tag} onClick={() => toggleArrayItem('activity_categories', tag)} className={`px-2 py-1 text-[10px] font-semibold rounded-md border transition ${form.activity_categories.includes(tag) ? 'bg-indigo-100 border-indigo-300 text-indigo-800 shadow-sm' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'}`}>
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Nút submit */}
            <div className="sticky bottom-0 bg-white pb-6 pt-4 z-20">
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-xl bg-slate-900 py-3.5 font-bold text-white shadow-lg transition hover:bg-blue-700 hover:shadow-blue-500/25 disabled:opacity-50 disabled:hover:bg-slate-900 flex justify-center items-center gap-2"
              >
                {loading ? (
                  <><div className="w-5 h-5 border-2 border-slate-400 border-t-white rounded-full animate-spin" /> Đang Phân Tích Dữ Liệu...</>
                ) : (
                  <><Settings2 className="w-5 h-5" /> Khởi Tạo Lịch Trình</>
                )}
              </button>
            </div>
          </form>

          {/* CỘT PHẢI: KẾT QUẢ RESPONSE DẠNG TEXT */}
          <section className="space-y-6">
            {response ? (
              <>
                <div className="flex items-center justify-between border-b-2 border-slate-200 pb-3">
                  <div className="flex gap-2">
                    <button onClick={() => setActiveTab('itinerary')} className={`px-5 py-2.5 rounded-xl text-sm font-bold transition shadow-sm ${activeTab === 'itinerary' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'}`}>
                      🗺️ Kế Hoạch Lịch Trình
                    </button>
                    <button onClick={() => setActiveTab('candidates')} className={`px-5 py-2.5 rounded-xl text-sm font-bold transition shadow-sm ${activeTab === 'candidates' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'}`}>
                      🏨 Dữ Liệu Ứng Viên ({response.candidates?.hotels?.length || 0})
                    </button>
                  </div>
                  <span className="text-[10px] font-black uppercase tracking-widest text-emerald-600 bg-emerald-100 px-3 py-1.5 rounded-lg border border-emerald-200 hidden sm:inline">
                    Status: {response.status}
                  </span>
                </div>

                {activeTab === 'itinerary' && (
                  <div className="space-y-8">
                    {/* BỘ LỌC CÁC PHƯƠNG ÁN */}
                    {itineraryOptions.length > 1 && (
                      <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm space-y-3">
                        <span className="text-sm font-extrabold text-slate-700 flex items-center gap-2 uppercase tracking-wide">
                           <MapPin className="w-4 h-4 text-rose-500"/> Các Phương Án Tối Ưu Nhất:
                        </span>
                        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                          {itineraryOptions.map((opt, idx) => (
                            <button key={idx} onClick={() => setSelectedOptionIndex(idx)} className={`p-4 text-left rounded-2xl border transition ${selectedOptionIndex === idx ? 'border-blue-600 bg-blue-50/60 ring-2 ring-blue-500' : 'border-slate-200 bg-slate-50 hover:bg-white hover:border-blue-300'}`}>
                              <p className="font-bold text-sm text-slate-800 leading-tight">{opt.option_name}</p>
                              <div className="flex flex-col mt-3 text-xs font-semibold text-slate-500 space-y-1.5">
                                <span className="flex justify-between items-center bg-white px-2 py-1 rounded shadow-sm border border-slate-100">Chi phí: <strong className="text-emerald-600 text-sm">${opt.summary_cost.total_cost_min}</strong></span>
                                <span className="flex justify-between items-center bg-white px-2 py-1 rounded shadow-sm border border-slate-100">Quãng đường: <strong className="text-rose-500">{opt.total_travel_distance_km} km</strong></span>
                              </div>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* VÙNG 1: HIỂN THỊ MARKDOWN */}
                    <MarkdownView result={response.markdown_itinerary} routes={response.map_routes} selectedFlight={selectedOption?.selected_flight} />
                  </div>
                )}

                {activeTab === 'candidates' && (
                  <div className="space-y-8 bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
                    <div className="space-y-4">
                      <h3 className="font-extrabold text-xl text-slate-800 flex items-center gap-2 border-b-2 pb-3">
                        <Hotel className="w-6 h-6 text-amber-500" /> Khách Sạn Đề Xuất
                      </h3>
                      <div className="grid gap-4 xl:grid-cols-2">
                        {response.candidates?.hotels?.map((hotel) => {
                          let parsedRaw: any = {};
                          try {
                            parsedRaw = typeof hotel.raw_data === 'string' ? JSON.parse(hotel.raw_data) : (hotel.raw_data || {});
                          } catch {
                            parsedRaw = {};
                          }
                          const img = hotel.primary_photo || parsedRaw.thumbnail || parsedRaw.images?.[0]?.original_image;
                          return (
                            <div key={hotel.fsq_place_id || hotel.name} className="bg-slate-50 p-4 rounded-2xl border border-slate-200 flex gap-4 hover:shadow-md transition">
                              {img && <img src={img} alt={hotel.name} className="w-24 h-24 rounded-xl object-cover shrink-0 shadow-sm" />}
                              <div className="space-y-1.5 text-xs">
                                <p className="font-extrabold text-sm text-slate-800 leading-tight">{hotel.name || parsedRaw.name}</p>
                                <p className="text-slate-500 truncate font-medium">{hotel.address || parsedRaw.address}</p>
                                <div className="flex gap-2 text-[10px] font-bold text-slate-600 bg-white p-1.5 rounded-lg border shadow-sm w-fit">
                                  {(hotel.has_wifi || JSON.stringify(parsedRaw).toLowerCase().includes('wifi')) && <span className="flex items-center gap-1"><Wifi className="w-3 h-3 text-blue-500"/> Wifi</span>}
                                  {(hotel.has_parking || JSON.stringify(parsedRaw).toLowerCase().includes('parking')) && <span className="flex items-center gap-1"><Car className="w-3 h-3 text-emerald-500"/> Đỗ xe</span>}
                                </div>
                                {(hotel.website || parsedRaw.link) && (
                                  <a href={hotel.website || parsedRaw.link} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-blue-600 font-bold hover:underline mt-1">
                                    Truy cập Website <ExternalLink className="w-3 h-3" />
                                  </a>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    <div className="space-y-4 pt-4">
                      <h3 className="font-extrabold text-xl text-slate-800 flex items-center gap-2 border-b-2 pb-3">
                        <Utensils className="w-6 h-6 text-emerald-500" /> Quán Ăn / Nhà Hàng
                      </h3>
                      <div className="grid gap-4 xl:grid-cols-2">
                        {response.candidates?.foods?.map((food) => {
                          let parsedFoodRaw: any = {};
                          try {
                            parsedFoodRaw = typeof food.raw_data === 'string' ? JSON.parse(food.raw_data) : (food.raw_data || {});
                          } catch {
                            parsedFoodRaw = {};
                          }
                          const foodImage = food.primary_photo || parsedFoodRaw.thumbnail || parsedFoodRaw.images?.[0]?.original_image;
                          return (
                          <div key={food.fsq_place_id || food.place_id} className="bg-slate-50 p-4 rounded-2xl border border-slate-200 flex gap-4 hover:shadow-md transition">
                            {foodImage && <img src={foodImage} alt={food.name || food.title || parsedFoodRaw.title} className="w-24 h-24 rounded-xl object-cover shrink-0 shadow-sm" />}
                            <div className="space-y-1.5 text-xs">
                              <p className="font-extrabold text-sm text-slate-800 leading-tight">{food.name || food.title || parsedFoodRaw.title}</p>
                              <p className="text-slate-500 truncate font-medium">{food.address || parsedFoodRaw.address}</p>
                              <div className="flex flex-wrap gap-1.5 mt-2">
                                {(food.tastes || []).slice(0, 4).map((t: string, i: number) => (
                                  <span key={i} className="bg-white border border-slate-200 px-2 py-1 rounded-md font-bold text-[9px] text-emerald-700 uppercase shadow-sm">{t}</span>
                                ))}
                              </div>
                            </div>
                          </div>
                        )})}
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="bg-white p-12 rounded-3xl border border-slate-200 text-center text-slate-500 space-y-4 h-full flex flex-col items-center justify-center min-h-[600px] shadow-sm">
                <div className="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center mb-2 border border-slate-100 shadow-inner">
                   <Compass className="w-12 h-12 text-blue-400 animate-spin-slow" />
                </div>
                <div>
                   <p className="text-lg font-black text-slate-700">Chưa có dữ liệu hành trình</p>
                   <p className="text-sm mt-2 text-slate-500 font-medium">Vui lòng điền thông tin bên trái và bấm nút khởi tạo để bắt đầu lập kế hoạch.</p>
                </div>
              </div>
            )}
          </section>
        </div>

        {/* VÙNG 2: HIỂN THỊ THÔNG TIN KHÁCH SẠN & DỮ LIỆU ĐỊA ĐIỂM CHI TIẾT */}
        {response && activeTab === 'itinerary' && primaryOption && (
          <section className="mt-8 pt-10 border-t-2 border-dashed border-slate-300 space-y-12">
            
            {/* 1. SECTION: KHÁCH SẠN ĐƯỢC CHỌN */}
            {(primaryOption as any).selected_hotel && (
              <HotelDetailSection hotel={(primaryOption as any).selected_hotel} />
            )}

            {/* 2. SECTION: HỒ SƠ ĐỊA ĐIỂM VUI CHƠI / QUÁN ĂN */}
            <div>
              <div className="mb-8">
                <h2 className="text-3xl font-black text-slate-800 flex items-center gap-3">
                  <Settings2 className="w-8 h-8 text-indigo-600" /> Hồ Sơ Địa Điểm Chi Tiết
                </h2>
                <p className="text-base text-slate-500 mt-2 font-medium max-w-3xl">
                  Bóc tách toàn bộ dữ liệu gốc (Raw API Data) dưới dạng Thẻ lồng Thẻ (Recursive Cards), cung cấp cái nhìn chuyên sâu và trực quan về mọi địa điểm trong hành trình.
                </p>
              </div>
              
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                 {(primaryOption as any).selected_activities?.map((act: any, i: number) => (
                   <PlaceDetailCard key={`act-${i}`} place={act} type="activity" />
                 ))}
                 {(primaryOption as any).selected_foods?.map((food: any, i: number) => (
                   <PlaceDetailCard key={`food-${i}`} place={food} type="food" />
                 ))}
              </div>
            </div>

          </section>
        )}
      </div>
    </main>
  );
}