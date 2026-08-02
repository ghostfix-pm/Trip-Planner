"use client";

import { useState } from "react";
import { Hotel, MapPin, ExternalLink } from "lucide-react";

export default function HotelDetailSection({ hotel }: { hotel: any }) {
  const allImages = hotel.images || [];
  const [activeImageIndex, setActiveImageIndex] = useState(0);

  const currentMainImg = 
    allImages[activeImageIndex]?.original_image || 
    allImages[activeImageIndex]?.thumbnail;

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm hover:shadow-md transition space-y-8">
      {/* Header: Tên, Hạng sao & Giá tiền */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-6">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="px-3 py-1 bg-amber-100 text-amber-800 text-[10px] font-black uppercase tracking-wider rounded-lg">
              {hotel.hotel_class || "Hotel"}
            </span>
            {hotel.overall_rating && (
              <span className="flex items-center gap-1 bg-blue-50 text-blue-700 px-2.5 py-1 rounded-lg text-xs font-bold border border-blue-100">
                ⭐ {hotel.overall_rating} <span className="text-slate-400 font-normal">({hotel.reviews} đánh giá)</span>
              </span>
            )}
          </div>
          <h2 className="text-3xl font-black text-slate-900 tracking-tight">{hotel.name}</h2>
          <p className="text-xs text-slate-500 font-medium">{hotel.description}</p>
        </div>

        {/* Khối hiển thị giá */}
        {hotel.total_rate && (
          <div className="bg-slate-50 border border-slate-200 px-5 py-3 rounded-2xl text-right shadow-sm self-start md:self-auto shrink-0">
            <span className="text-[10px] font-bold text-slate-400 uppercase block">Tổng chi phí ({hotel.total_rate.lowest})</span>
            <div className="flex items-baseline gap-1.5 justify-end mt-0.5">
              <span className="text-2xl font-black text-emerald-600">{hotel.total_rate.lowest}</span>
              <span className="text-xs text-slate-500 font-medium">({hotel.rate_per_night?.lowest}/đêm)</span>
            </div>
          </div>
        )}
      </div>

      {/* Grid Hình ảnh & Thông tin cốt lõi */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Thư viện ảnh tương tác bên trái */}
        <div className="lg:col-span-5 space-y-3">
          {currentMainImg ? (
            <div className="relative rounded-2xl overflow-hidden border border-slate-200 shadow-sm group bg-slate-900">
              <img 
                src={currentMainImg} 
                alt={hotel.name} 
                className="w-full h-72 object-cover transition duration-300 group-hover:scale-105" 
              />
              <div className="absolute bottom-3 right-3 bg-black/60 backdrop-blur-md text-white text-[10px] font-bold px-2.5 py-1 rounded-lg">
                Ảnh {activeImageIndex + 1} / {allImages.length}
              </div>
            </div>
          ) : (
            <div className="w-full h-72 rounded-2xl bg-slate-100 flex items-center justify-center text-slate-400">
              <Hotel className="w-12 h-12" />
            </div>
          )}
          
          {/* Danh sách ảnh thu nhỏ để bấm chuyển đổi */}
          {allImages.length > 1 && (
            <div className="grid grid-cols-5 gap-2 overflow-x-auto pb-1">
              {allImages.slice(0, 5).map((img: any, idx: number) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setActiveImageIndex(idx)}
                  className={`rounded-xl overflow-hidden border-2 transition h-14 w-full relative ${
                    activeImageIndex === idx ? 'border-blue-600 ring-2 ring-blue-500/20 scale-95' : 'border-slate-200 opacity-70 hover:opacity-100'
                  }`}
                >
                  <img src={img.thumbnail} alt="thumb" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Thông tin chi tiết bên phải */}
        <div className="lg:col-span-7 space-y-6">
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-100">
              <span className="text-[10px] font-bold uppercase text-slate-400 block">Thời gian nhận phòng</span>
              <span className="text-sm font-extrabold text-slate-800 mt-0.5 block">🕒 Từ {hotel.check_in_time}</span>
            </div>
            <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-100">
              <span className="text-[10px] font-bold uppercase text-slate-400 block">Thời gian trả phòng</span>
              <span className="text-sm font-extrabold text-slate-800 mt-0.5 block">🕒 Trước {hotel.check_out_time}</span>
            </div>
          </div>

          {/* Đánh giá chi tiết */}
          {hotel.reviews_breakdown && hotel.reviews_breakdown.length > 0 && (
            <div className="space-y-2">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wide">Điểm nổi bật từ đánh giá</span>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {hotel.reviews_breakdown.map((item: any, idx: number) => (
                  <div key={idx} className="bg-slate-50/70 border border-slate-100 p-2.5 rounded-xl text-xs">
                    <span className="font-bold text-slate-700 block">{item.name}</span>
                    <span className="text-[11px] text-emerald-600 font-semibold mt-0.5 block">
                      👍 {item.positive} / <span className="text-slate-400">{item.total_mentioned} đề cập</span>
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tiện ích */}
          {hotel.amenities && hotel.amenities.length > 0 && (
            <div className="space-y-2">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wide">Tiện ích chỗ ở</span>
              <div className="flex flex-wrap gap-1.5">
                {hotel.amenities.map((amenity: string, idx: number) => (
                  <span key={idx} className="px-2.5 py-1 bg-blue-50/60 border border-blue-100 text-blue-800 text-xs font-semibold rounded-lg">
                    ✓ {amenity}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Địa điểm lân cận */}
      {hotel.nearby_places && hotel.nearby_places.length > 0 && (
        <div className="border-t border-slate-100 pt-6 space-y-3">
          <span className="text-xs font-bold text-slate-700 uppercase tracking-wide flex items-center gap-1.5">
            <MapPin className="w-4 h-4 text-rose-500" /> Các địa điểm lân cận & Thời gian di chuyển
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {hotel.nearby_places.map((place: any, idx: number) => (
              <div key={idx} className="bg-slate-50 border border-slate-200/60 p-3 rounded-2xl space-y-1.5">
                <p className="font-bold text-xs text-slate-800 line-clamp-1">{place.name}</p>
                <div className="flex flex-wrap gap-1">
                  {place.transportations?.map((t: any, tIdx: number) => (
                    <span key={tIdx} className="text-[10px] bg-white border border-slate-200 px-2 py-0.5 rounded-md font-medium text-slate-600">
                      {t.type === 'Walking' ? '🚶 Bộ' : '🚕 Taxi'}: <strong className="text-slate-800">{t.duration}</strong>
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Nút hành động */}
      {hotel.link && (
        <div className="border-t border-slate-100 pt-5 flex justify-end">
          <a 
            href={hotel.link} 
            target="_blank" 
            rel="noreferrer" 
            className="inline-flex items-center gap-2 px-6 py-3 bg-slate-900 text-white text-xs font-bold rounded-xl hover:bg-blue-600 transition shadow-sm hover:shadow-md"
          >
            Xem chi tiết trên Google Hotels <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      )}
    </div>
  );
}