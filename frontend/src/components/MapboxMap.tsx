'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';

interface MapPoint {
  id: string;
  name: string;
  type: string;
  day: number;
  order: number;
  latitude: number;
  longitude: number;
  address?: string;
}

interface DayRoute {
  day: number;
  waypoints: MapPoint[];
}

// Import MapContainer & Marker dynamic để không bị lỗi SSR trong Next.js
const LeafletMapInner = dynamic(() => import('./LeafletMapInner'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-100 flex items-center justify-center bg-slate-100 text-slate-500 text-sm">
      Đang tải bản đồ lộ trình...
    </div>
  ),
});

export default function MapboxMap({ routes }: { routes: DayRoute[] }) {
  const [selectedDay, setSelectedDay] = useState<number>(1);

  if (!routes || routes.length === 0) {
    return (
      <div className="p-4 text-sm text-slate-500 bg-slate-100 rounded-lg text-center">
        Chưa có dữ liệu tọa độ để hiển thị bản đồ.
      </div>
    );
  }

  const currentRoute = routes.find((r) => r.day === selectedDay) || routes[0];
  const waypoints = currentRoute?.waypoints || [];

  return (
    <div className="w-full rounded-2xl overflow-hidden border border-slate-200 shadow-sm bg-white my-4">
      {/* Header chọn Ngày */}
      <div className="flex items-center justify-between p-3 bg-slate-50 border-b border-slate-200">
        <span className="text-xs font-bold text-slate-700">
          🗺️ Lộ trình Ngày {selectedDay} ({waypoints.length} điểm)
        </span>
        <div className="flex gap-1.5">
          {routes.map((r) => (
            <button
              key={r.day}
              onClick={() => setSelectedDay(r.day)}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${
                selectedDay === r.day
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
              }`}
            >
              Ngày {r.day}
            </button>
          ))}
        </div>
      </div>

      {/* Bản đồ Leaflet */}
      <div className="w-full h-100 relative">
        <LeafletMapInner waypoints={waypoints} />
      </div>

      {/* Danh sách địa điểm bên dưới */}
      <div className="p-3 bg-slate-50/50 border-t border-slate-200 max-h-40 overflow-y-auto text-xs space-y-1.5">
        {waypoints.map((point, index) => (
          <div key={`${point.id}-${index}`} className="flex items-center gap-2 text-slate-600">
            <span
              className={`w-5 h-5 flex items-center justify-center rounded-full text-[10px] font-bold text-white shrink-0 ${
                point.type === 'hotel'
                  ? 'bg-amber-500'
                  : point.type === 'food'
                  ? 'bg-emerald-500'
                  : 'bg-blue-500'
              }`}
            >
              {index + 1}
            </span>
            <span className="font-medium text-slate-800">{point.name}</span>
            {point.address && <span className="text-slate-400 truncate">({point.address})</span>}
          </div>
        ))}
      </div>
    </div>
  );
}