// src/services/api.ts

// 1. CẤU HÌNH ĐỊA CHỈ BACKEND
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

// ==========================================
// 2. KHAI BÁO CÁC KIỂU DỮ LIỆU (INTERFACES)
// ==========================================

export interface TravelPlannerRequest {
  origin: string;
  destination: string;
  duration_days: number;
  min_budget?: number;
  max_budget: number;
  num_adults: number;
  num_children: number;
  num_infants: number;
  num_elderly: number;
  
  // Hotel specs
  hotel_price_level?: string;
  hotel_requirements?: string;
  // Food specs
  food_price_level?: string;
  food_categories?: string[];
  
  attractions_categories?: string[];
  travel_pace?: string;
}


export interface TripRequest {
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
  food_price_level: string;
  food_categories: string[];
  activity_categories: string[];
  flight_class: string;
  non_stop_only: boolean;
  travel_pace: string;
}

export interface ItineraryOption {
  option_name: string;
  summary_cost: {
    flight_cost?: number;
    hotel_cost?: number;
    activity_cost?: number;
    estimated_food_cost_min?: number;
    estimated_food_cost_max?: number;
    estimated_transport_cost?: number;
    total_cost_min?: number;
    total_cost_max?: number;
    total_cost?: number | string; // Dự phòng cho TH backend cũ
  };
  total_travel_distance_km: number;
  
  // 👇 THÊM CÁC DÒNG NÀY VÀO ĐỂ TYPESCRIPT HẾT BÁO LỖI 👇
  selected_activities?: any[];
  selected_foods?: any[];
  selected_hotel?: any;
  selected_flight?: any;
}

export interface TravelPlannerResponse {
  status: string;
  itinerary_options?: ItineraryOption[];
  markdown_itinerary?: string;
  map_routes?: any[];
  candidates?: {
    hotels?: any[];
    foods?: any[];
    flight?: any[];
    activity?: any[];
  };
  tripId?: string; // Server có thể trả về Trip ID từ Header hoặc Body
}

// ==========================================
// 3. API SERVICE CHO PLANNER
// ==========================================

export const tripApi = {
  // Hàm 1: Lấy danh sách Tags
  async getTagsConfig() {
    const res = await fetch(`${API_URL}/tag_config`);
    if (!res.ok) {
      throw new Error("Không thể tải cấu hình tag từ Backend");
    }
    return res.json();
  },

  // Hàm 2: Plan Trip
  async planTrip(data: TripRequest): Promise<any> {
    let token = null;
    if (typeof window !== 'undefined') token = localStorage.getItem('access_token');

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_URL}/plan-trip`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      if (response.status === 401) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        throw new Error('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
      }
      const errorData = await response.json().catch(() => ({}));

      if (response.status === 422) {
        console.error("🚨 Chi tiết lỗi 422 từ FastAPI:", errorData.detail);
        throw new Error("Lỗi xác thực dữ liệu: " + JSON.stringify(errorData.detail));
      }

      throw new Error(errorData.detail || 'Đã có lỗi xảy ra khi tạo lịch trình');
    }

    const result = await response.json();
    const tripIdFromHeader = response.headers.get('X-Trip-Id');
    if (tripIdFromHeader) result.tripId = tripIdFromHeader;

    return result;
  },

  /**
   * Hàm gọi API lấy chi tiết chuyến đi đã lưu. Đòi hỏi Token xác thực.
   */
  async getTrip(tripId: string): Promise<any> {
    let token = null;
    if (typeof window !== 'undefined') {
      token = localStorage.getItem('access_token');
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}/trips/${tripId}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        throw new Error('Vui lòng đăng nhập để xem lịch trình.');
      }
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Không thể tải chi tiết chuyến đi.');
    }

    return response.json();
  }
};