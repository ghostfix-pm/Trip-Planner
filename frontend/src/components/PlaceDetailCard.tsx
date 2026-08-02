"use client";

import { Settings2 } from "lucide-react";

const IGNORED_KEYS = [
  'position', 'title', 'place_id', 'data_id', 'data_cid', 
  'reviews_link', 'photos_link', 'gps_coordinates', 'thumbnail', 
  'type', 'types', 'type_id', 'type_ids', 'address', 'rating', 'reviews','extracted_price',
  'place_id_search', 'provider_id', 'service_options', 'serpapi_thumbnail', 'unclaimed_listing'
];

function RecursiveCard({ data, level = 0 }: { data: any, level?: number }) {
  if (data === null || data === undefined) return null;

  if (typeof data !== 'object') {
    const text = String(data);
    if (text.startsWith('http')) return <a href={text} target="_blank" rel="noreferrer" className="text-blue-500 hover:underline truncate max-w-full inline-block">{text}</a>;
    return <span className="text-slate-700 font-medium">{text}</span>;
  }

  if (Array.isArray(data)) {
    return (
      <div className="flex flex-wrap gap-2 mt-1">
        {data.map((item, i) => {
          if (item === null || item === '') return null;
          return (
            <div key={i} className={`rounded-lg px-2.5 py-1 text-xs font-semibold border shadow-sm ${level % 2 === 0 ? 'bg-indigo-50 border-indigo-100 text-indigo-800' : 'bg-emerald-50 border-emerald-100 text-emerald-800'}`}>
              <RecursiveCard data={item} level={level + 1} />
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2 mt-1.5">
      {Object.entries(data).map(([key, value]) => {
        if (level === 0 && IGNORED_KEYS.includes(key)) return null; 
        if (value === null || value === '' || (Array.isArray(value) && value.length === 0)) return null;
        
        return (
          <div key={key} className="bg-white border border-slate-200 shadow-sm rounded-xl p-3 hover:shadow-md transition">
            <span className="block text-[10px] font-extrabold uppercase tracking-wider text-slate-400 mb-1.5">
              {key.replace(/_/g, ' ')}
            </span>
            <RecursiveCard data={value} level={level + 1} />
          </div>
        );
      })}
    </div>
  );
}

export default function PlaceDetailCard({ place, type }: { place: any, type: string }) {
  let parsedRaw = {};
  try {
    if (typeof place.raw_data === 'string') {
      parsedRaw = JSON.parse(place.raw_data);
    } else if (place.raw_data && typeof place.raw_data === 'object') {
      parsedRaw = place.raw_data;
    } else if (place && typeof place === 'object') {
      parsedRaw = place;
    }
  } catch (e) {}

  const thumbnail =
    place.primary_photo ||
    (parsedRaw as any).thumbnail ||
    (parsedRaw as any).images?.[0]?.original_image ||
    (parsedRaw as any).images?.[0]?.thumbnail;

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-5 shadow-sm flex flex-col gap-4 overflow-hidden relative transition hover:shadow-md h-fit max-h-200">
      <div className="flex gap-4 items-start">
         {thumbnail && <img src={thumbnail} alt="thumbnail" className="w-20 h-20 rounded-2xl object-cover shadow-sm shrink-0" />}
         <div>
           <h4 className="font-bold text-base text-slate-800 leading-tight">
             {place.name || (parsedRaw as any).name || (parsedRaw as any).title}
           </h4>
           <span className={`inline-block px-2.5 py-1 mt-2 rounded-lg text-[10px] font-bold uppercase tracking-wide ${type === 'activity' ? 'bg-blue-100 text-blue-700' : 'bg-rose-100 text-rose-700'}`}>
             {type === 'activity' ? 'Vui chơi / Khám phá' : 'Ăn uống / Nhà hàng'}
           </span>
         </div>
      </div>
      
      <div className="text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100 shadow-inner">
         <p className="flex items-center gap-1">⭐ <strong className="text-slate-800 text-sm">{place.rating || (parsedRaw as any).rating || 'N/A'}</strong> ({place.reviews || (parsedRaw as any).reviews || 0} đánh giá)</p>
         <p className="mt-1.5 line-clamp-2 leading-relaxed">📍 {place.address || (parsedRaw as any).address || 'Đang cập nhật địa chỉ'}</p>
      </div>

      <div className="mt-2 flex-1 overflow-hidden flex flex-col">
        <h5 className="text-xs font-bold text-slate-700 mb-2 flex items-center gap-1.5">
          <Settings2 className="w-4 h-4 text-blue-500"/> Thuộc tính mở rộng (Raw API)
        </h5>
        <div className="overflow-y-auto custom-scrollbar pr-2 pb-2 h-full rounded-xl bg-slate-50 p-2 border border-slate-100">
          <RecursiveCard data={parsedRaw} />
        </div>
      </div>
    </div>
  );
}