'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import MapboxMap from './MapboxMap';
import { Plane, Clock, Tag } from 'lucide-react';

interface MarkdownViewProps {
  result: any;
  routes?: any[];
  selectedFlight?: any; // Thêm prop nhận thông tin chuyến bay
}

export default function MarkdownView({ result, routes, selectedFlight }: MarkdownViewProps) {
  let markdownContent = '';
  let mapRoutes: any[] = routes || [];
  let flightInfo = selectedFlight;

  const pickMarkdown = (data: any) =>
    data?.markdown_itinerary ||
    data?.final_itinerary_markdown ||
    data?.plan?.markdown_itinerary ||
    data?.plan?.final_itinerary_markdown ||
    '';

  const pickRoutes = (data: any) =>
    data?.map_routes ||
    data?.plan?.map_routes ||
    [];

  const pickFlight = (data: any) =>
    data?.selected_flight ||
    data?.plan?.selected_flight ||
    null;

  if (typeof result === 'string') {
    try {
      const parsed = JSON.parse(result);
      markdownContent = pickMarkdown(parsed) || result;
      if (mapRoutes.length === 0) {
        mapRoutes = pickRoutes(parsed);
      }
      if (!flightInfo) {
        flightInfo = pickFlight(parsed);
      }
    } catch {
      markdownContent = result;
    }
  } else if (typeof result === 'object' && result !== null) {
    markdownContent = pickMarkdown(result);
    if (mapRoutes.length === 0) {
      mapRoutes = pickRoutes(result);
    }
    if (!flightInfo) {
      flightInfo = pickFlight(result);
    }
  }

  let cleanedMarkdown = markdownContent.trim();
  if (cleanedMarkdown.startsWith('```markdown')) {
    cleanedMarkdown = cleanedMarkdown.replace(/^```markdown\s*/i, '');
  }
  if (cleanedMarkdown.endsWith('```')) {
    cleanedMarkdown = cleanedMarkdown.replace(/\s*```$/, '');
  }

  return (
    <div className="bg-white p-6 md:p-8 rounded-3xl shadow-sm border border-slate-200 prose prose-slate max-w-none prose-headings:font-bold prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h3: ({ node, children, ...props }: any) => (
            <h3 className="text-xl font-extrabold text-slate-800 mt-10 mb-4 flex items-center gap-3 border-b-2 border-slate-100 pb-3" {...props}>
              <span className="bg-blue-600 w-2.5 h-7 rounded-full inline-block shadow-sm"></span>
              {children}
            </h3>
          ),
          h4: ({ node, children, ...props }: any) => (
            <h4 className="text-lg font-bold text-slate-700 mt-6 mb-2 flex items-center gap-2" {...props}>
              <span className="border-4 border-emerald-400 w-3.5 h-3.5 rounded-full inline-block"></span>
              {children}
            </h4>
          ),
          blockquote: ({ node, children, ...props }: any) => (
            <blockquote className="bg-blue-50/50 border-l-4 border-blue-500 p-5 rounded-2xl rounded-l-none my-5 text-sm text-slate-700 shadow-sm not-prose" {...props}>
              {children}
            </blockquote>
          ),
          p: ({ node, children, ...props }: any) => {
            return (
              <div className="mb-4 text-slate-600 leading-relaxed" {...props}>
                {children}
              </div>
            );
          },
          code({ node, inline, className, children, ...props }: any) {
            const rawText = String(children || '').trim();
            const isMapboxEmbed =
              className?.includes('mapbox-embed') ||
              rawText.includes('mapbox-embed') ||
              /language-`*mapbox-embed`*/i.test(className || '');

            if (!inline && isMapboxEmbed) {
              const firstFlight = flightInfo?.flights?.[0];

              return (
                <div className="my-8 not-prose space-y-6">
                  {/* PHẦN HIỂN THỊ THÔNG TIN CHUYẾN BAY NẰM TRÊN BẢN ĐỒ */}
                  {flightInfo && (
                    <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                        <div className="flex items-center gap-2">
                          {flightInfo.airline_logo && (
                            <img src={flightInfo.airline_logo} alt="Airline logo" className="w-6 h-6 object-contain" />
                          )}
                          <span className="font-extrabold text-sm text-slate-800 flex items-center gap-1.5">
                            <Plane className="w-4 h-4 text-blue-600" /> Thông Tin Chuyến Bay ({flightInfo.type || 'Standard'})
                          </span>
                        </div>
                        <span className="text-xs font-bold text-emerald-600 bg-emerald-100 px-2.5 py-1 rounded-lg">
                          ${flightInfo.price}
                        </span>
                      </div>

                      <div className="grid gap-3 sm:grid-cols-3 text-xs">
                        <div className="bg-white p-3 rounded-xl border border-slate-100 shadow-sm">
                          <span className="text-slate-400 font-bold uppercase block text-[10px]">Khởi hành</span>
                          <p className="font-bold text-slate-800 mt-1">{firstFlight?.departure_airport?.name || 'N/A'} ({firstFlight?.departure_airport?.id})</p>
                          <p className="text-slate-500 mt-0.5">{firstFlight?.departure_airport?.time}</p>
                        </div>
                        <div className="bg-white p-3 rounded-xl border border-slate-100 shadow-sm flex flex-col justify-center items-center text-center">
                          <span className="text-slate-400 font-bold uppercase text-[10px] flex items-center gap-1">
                            <Clock className="w-3 h-3 text-blue-500" /> Tổng thời gian
                          </span>
                          <p className="font-extrabold text-slate-800 mt-1">{flightInfo.total_duration} phút</p>
                        </div>
                        <div className="bg-white p-3 rounded-xl border border-slate-100 shadow-sm">
                          <span className="text-slate-400 font-bold uppercase block text-[10px]">Đến nơi</span>
                          <p className="font-bold text-slate-800 mt-1">{firstFlight?.arrival_airport?.name || 'N/A'} ({firstFlight?.arrival_airport?.id})</p>
                          <p className="text-slate-500 mt-0.5">{firstFlight?.arrival_airport?.time}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* BẢN ĐỒ MAPBOX */}
                  <div className="rounded-2xl overflow-hidden border border-slate-200 shadow-lg ring-4 ring-slate-50">
                    <MapboxMap routes={mapRoutes} />
                  </div>
                </div>
              );
            }

            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {cleanedMarkdown || 'No itinerary content available.'}
      </ReactMarkdown>
    </div>
  );
}