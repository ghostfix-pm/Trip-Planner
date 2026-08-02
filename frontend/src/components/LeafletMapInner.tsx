'use client';

import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

const customIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function LeafletMapInner({ waypoints }: { waypoints: any[] }) {
  if (!waypoints || waypoints.length === 0) return null;

  const positions = waypoints.map((p) => [p.latitude, p.longitude] as [number, number]);
  const center = positions[0];

  return (
    <MapContainer center={center} zoom={14} style={{ height: '100%', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap'
      />
      <Polyline positions={positions} color="#2563eb" weight={4} opacity={0.7} dashArray="6, 8" />
      {waypoints.map((point, idx) => (
        <Marker key={`${point.id}-${idx}`} position={[point.latitude, point.longitude]} icon={customIcon}>
          <Popup>
            <div className="text-xs font-sans">
              <p className="font-bold text-slate-800">{idx + 1}. {point.name}</p>
              <p className="text-slate-500">{point.address}</p>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}