from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class CandidateData(BaseModel):
    flights: List[Dict[str, Any]] = Field(default_factory=list)
    hotels: List[Dict[str, Any]] = Field(default_factory=list)
    foods: List[Dict[str, Any]] = Field(default_factory=list)
    activities: List[Dict[str, Any]] = Field(default_factory=list)


class TravelPlanResponse(BaseModel):
    status: str = Field(..., description="Trạng thái xử lý lộ trình")
    message: str = Field(..., description="Thông báo trả về cho frontend")
    user_intent: Dict[str, Any] = Field(default_factory=dict, description="Dữ liệu intent sau chuẩn hóa")
    itinerary_options: List[Dict[str, Any]] = Field(default_factory=list, description="Danh sách các phương án lộ trình")
    markdown_itinerary: str = Field(default="", description="Bản markdown timeline cuối cùng")
    map_routes: List[Dict[str, Any]] = Field(default_factory=list, description="Danh sách route mapbox theo ngày")
    candidates: CandidateData = Field(default_factory=CandidateData, description="Danh sách candidates theo từng loại")
    agent_messages: List[str] = Field(default_factory=list, description="Log message từ các agent")


class TripSummaryResponse(BaseModel):
    id: str = Field(..., description="ID của chuyến đi")
    origin: str = Field(..., description="Điểm xuất phát")
    destination: str = Field(..., description="Điểm đến")
    duration_days: int = Field(..., description="Số ngày")
    max_budget: float = Field(..., description="Ngân sách tối đa")
    total_estimated_cost: float = Field(..., description="Chi phí ước tính")
    is_within_budget: bool = Field(..., description="Có nằm trong ngân sách không")
    created_at: datetime = Field(..., description="Thời điểm tạo")


TripResponse = TravelPlanResponse
