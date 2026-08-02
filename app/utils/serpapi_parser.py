# app/utils/serpapi_parser.py
from typing import Dict, Any, List

class SerpApiParser:
    """
    Trình bóc tách dữ liệu JSON từ SerpApi sang định dạng chuẩn của Database Models.
    Sử dụng .get() để chống lỗi KeyError khi thiếu dữ liệu.
    """

    @staticmethod
    def parse_hotel(raw_hotel: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bóc tách JSON Khách sạn (từ Google Hotels)
        Khớp với schema của HotelModel trong models.py
        """
        gps = raw_hotel.get("gps_coordinates", {})
        
        return {
            "type": raw_hotel.get("type"),
            "name": raw_hotel.get("name", "Khách sạn chưa rõ tên"),
            "description": raw_hotel.get("description"),
            "link": raw_hotel.get("link"),
            
            # Tọa độ
            "latitude": gps.get("latitude"),
            "longitude": gps.get("longitude"),
            
            # Thời gian
            "check_in_time": raw_hotel.get("check_in_time"),
            "check_out_time": raw_hotel.get("check_out_time"),
            
            # Giá và Hạng
            "rate_per_night": raw_hotel.get("rate_per_night"),
            "total_rate": raw_hotel.get("total_rate"),
            "extracted_hotel_class": raw_hotel.get("extracted_hotel_class"),
            
            # Đánh giá (Rating)
            "overall_rating": raw_hotel.get("overall_rating"),
            "reviews": raw_hotel.get("reviews"),
            "ratings_5_stars": raw_hotel.get("ratings_5_stars"),
            "ratings_4_stars": raw_hotel.get("ratings_4_stars"),
            "ratings_3_stars": raw_hotel.get("ratings_3_stars"),
            "ratings_2_stars": raw_hotel.get("ratings_2_stars"),
            "ratings_1_stars": raw_hotel.get("ratings_1_stars"),
            "location_rating": raw_hotel.get("location_rating"),
            "reviews_breakdown": raw_hotel.get("reviews_breakdown"),
            
            # Dữ liệu mảng/Json khác
            "nearby_places": raw_hotel.get("nearby_places"),
            "images": raw_hotel.get("images"),
            "amenities": raw_hotel.get("amenities"),
            
            # Lưu lại nguyên bản
            "raw_data": raw_hotel
        }

    @staticmethod
    def parse_destination(raw_place: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bóc tách JSON Điểm đến: Quán ăn & Vui chơi (từ Google Maps)
        Khớp với schema của DestinationModel trong models.py
        """
        gps = raw_place.get("gps_coordinates", {})
        op_hours = raw_place.get("operating_hours", {})
        
        return {
            # Khóa chính
            "place_id": raw_place.get("place_id"),
            
            "title": raw_place.get("title", "Địa điểm chưa rõ tên"),
            
            # Tọa độ
            "gps_coordinates": gps,
            "latitude": gps.get("latitude"),
            "longitude": gps.get("longitude"),
            
            # Đánh giá
            "rating": raw_place.get("rating"),
            "reviews": raw_place.get("reviews"),
            
            # Phân loại
            "type": raw_place.get("type"),
            "types": raw_place.get("types"),
            "type_id": raw_place.get("type_id"),
            "type_ids": raw_place.get("type_ids"),
            
            # Thông tin liên hệ
            "address": raw_place.get("address"),
            "country": raw_place.get("country"),
            "phone": raw_place.get("phone"),
            "website": raw_place.get("website"),
            
            # Lịch hoạt động từng ngày
            "operating_hours_monday": op_hours.get("monday"),
            "operating_hours_tuesday": op_hours.get("tuesday"),
            "operating_hours_wednesday": op_hours.get("wednesday"),
            "operating_hours_thursday": op_hours.get("thursday"),
            "operating_hours_friday": op_hours.get("friday"),
            "operating_hours_saturday": op_hours.get("saturday"),
            "operating_hours_sunday": op_hours.get("sunday"),
            
            # Các tính năng / Tiện ích mở rộng
            "extensions": raw_place.get("extensions"),
            "unsupported_extensions": raw_place.get("unsupported_extensions"),
            "service_options": raw_place.get("service_options"),
            
            # Hình ảnh & Đặt bàn
            "thumbnail": raw_place.get("thumbnail"),
            "user_review": raw_place.get("user_review"),
            "reserve_a_table": raw_place.get("reserve_a_table"),
            
            # Lưu lại nguyên bản
            "raw_data": raw_place
        }

    @classmethod
    def parse_hotels_list(cls, raw_hotels_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Hàm hỗ trợ bóc tách một mảng nhiều Khách sạn"""
        return [cls.parse_hotel(h) for h in raw_hotels_list]

    @classmethod
    def parse_destinations_list(cls, raw_destinations_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Hàm hỗ trợ bóc tách một mảng nhiều Điểm đến (Food/Activity)"""
        # Lọc bỏ các kết quả không có place_id (vì place_id là khóa chính trong DB)
        valid_destinations = [d for d in raw_destinations_list if d.get("place_id")]
        return [cls.parse_destination(d) for d in valid_destinations]