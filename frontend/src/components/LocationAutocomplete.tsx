"use client";

import { useState, useEffect } from "react";

const FALLBACK_CITIES = [
  { name: "Hà Nội", iata: "HAN", region: "", country: "Vietnam" },
  { name: "Hồ Chí Minh", iata: "SGN", region: "", country: "Vietnam" },
  { name: "Đà Nẵng", iata: "DAD", region: "", country: "Vietnam" },
  { name: "Phú Quốc", iata: "PQC", region: "", country: "Vietnam" },
  { name: "Nha Trang", iata: "CXR", region: "", country: "Vietnam" },
  { name: "Đà Lạt", iata: "DLI", region: "", country: "Vietnam" },
  { name: "Hải Phòng", iata: "HPH", region: "", country: "Vietnam" },
  { name: "Bangkok", iata: "BKK", region: "", country: "Thailand" },
  { name: "Singapore", iata: "SIN", region: "", country: "Singapore" },
  { name: "Seoul", iata: "ICN", region: "", country: "South Korea" },
  { name: "Tokyo", iata: "HND", region: "", country: "Japan" },
  { name: "Osaka", iata: "KIX", region: "", country: "Japan" },
  { name: "Taipei", iata: "TPE", region: "", country: "Taiwan" },
  { name: "Paris", iata: "CDG", region: "", country: "France" },
  { name: "London", iata: "LHR", region: "", country: "United Kingdom" },
  { name: "New York", iata: "JFK", region: "NY", country: "United States" },
  { name: "Washington DC", iata: "IAD", region: "DC", country: "United States" },
  { name: "Los Angeles", iata: "LAX", region: "CA", country: "United States" },
  { name: "Sydney", iata: "SYD", region: "NSW", country: "Australia" }
];

export default function LocationAutocomplete({ 
  value, 
  onChange, 
  placeholder, 
  cities = [] 
}: { 
  value: string; 
  onChange: (v: string) => void; 
  placeholder: string;
  cities?: any[];
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState(value);

  useEffect(() => { setSearch(value); }, [value]);

  const activeCities = cities && cities.length > 0 ? cities : FALLBACK_CITIES;

  const filtered = activeCities.filter(c =>
    (c.name || '').toLowerCase().includes(search.toLowerCase()) ||
    (c.country || '').toLowerCase().includes(search.toLowerCase()) ||
    (c.iata || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="relative w-full">
      <input
        type="text"
        className="w-full rounded-xl border border-slate-300 px-3 py-2 bg-slate-50 focus:bg-white transition outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
        placeholder={placeholder}
        value={search}
        onChange={(e) => {
          const val = e.target.value;
          setSearch(val);
          onChange(val);
          setIsOpen(true);
        }}
        onFocus={() => setIsOpen(true)}
        onBlur={() => setTimeout(() => setIsOpen(false), 200)}
        required
      />
      {isOpen && search.length > 0 && filtered.length > 0 && (
        <div className="absolute top-full left-0 w-full mt-1.5 bg-white border border-slate-200 shadow-2xl rounded-xl max-h-60 overflow-y-auto z-100">
          {filtered.map((c, i) => {
            const fullText = [c.name, c.region, c.country].filter(Boolean).join(", ");
            return (
              <div
                key={i}
                className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-slate-100 last:border-0 transition"
                onClick={() => {
                  onChange(fullText);
                  setSearch(fullText);
                  setIsOpen(false);
                }}
              >
                <div className="flex justify-between items-center">
                  <span className="font-bold text-slate-800 text-sm">{c.name}</span>
                  <span className="text-[10px] font-bold text-blue-600 bg-blue-100 px-2 py-0.5 rounded">{c.iata}</span>
                </div>
                <div className="text-xs text-slate-500 mt-1 font-medium">
                  {[c.region, c.country].filter(Boolean).join(", ")}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}