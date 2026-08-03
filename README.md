# 🗺️ Trip Planner - Autonomous Multi-Agent Travel Planner

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/Agents-LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/langgraph)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

> **Trip Planner** là hệ thống lập kế hoạch du lịch tự động sử dụng **multi-agent** (LangGraph) kết hợp **FastAPI**: người dùng nhập nhu cầu (điểm đi, điểm đến, ngân sách, sở thích), hệ thống tự động tìm chuyến bay, khách sạn, món ăn và điểm tham quan, sau đó tối ưu lộ trình và tổng hợp thành một bản kế hoạch chi tiết.

---

## ✨ Tính Năng Chính

- 🤖 **Multi-agent pipeline**: các agent chuyên biệt xử lý từng khâu — trích xuất ý định, tìm chuyến bay (Google Flights), tìm khách sạn (Google Hotels), tìm điểm ăn uống & tham quan (Google Maps), phân cụm địa điểm theo ngày, tối ưu chi phí & lộ trình (TSP + Mapbox Matrix), tổng hợp lịch trình cuối cùng bằng LLM.
- 🗺️ **Bản đồ & lộ trình**: sinh route Mapbox theo từng ngày và link Google Maps dẫn đường giữa các điểm.
- 💰 **Tối ưu ngân sách**: tính toán chi phí chuyến bay, khách sạn, ăn uống, di chuyển; tự động chọn phương án nằm trong ngân sách.
- 🧠 **Bayesian rating**: xếp hạng địa điểm theo công thức trung bình có trọng số (rating + số lượng review).
- ⚡ **Cache thông minh**: lưu cache kết quả SerpApi theo TTL động (chuyến bay gần ngày đi cache ngắn, xa ngày cache dài).
- 🔐 **Xác thực JWT**: đăng ký / đăng nhập, access token + refresh token.
- 📱 **Frontend Next.js**: form nhập nhu cầu, hiển thị lịch trình markdown, bản đồ Leaflet/Mapbox.

---

## 🛠️ Công Nghệ Sử Dụng

| Thành phần | Công nghệ |
|---|---|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| Agent orchestration | LangGraph, LangChain |
| Dữ liệu | SQLite + SQLAlchemy (async, aiosqlite) |
| External APIs | SerpApi (flights/hotels/maps), Mapbox Matrix, OpenAI |
| Frontend | Next.js, React, Leaflet, Tailwind CSS |
| Bảo mật | JWT (python-jose), bcrypt (passlib) |

---

## 🏗️ Kiến Trúc Agent Pipeline

```text
                    ┌─────────────────────┐
                    │  intent_extractor   │
                    └──────────┬──────────┘
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
   ┌─────────────────┐ ┌─────────────┐ ┌──────────────┐
   │   flight_agent  │ │ hotel_agent │ │activity_agent│
   └─────────────────┘ └─────────────┘ └──────┬───────┘
             │                │                ▼
             │                │        ┌──────────────┐
             │                │        │cluster_agent │
             │                │        └──────┬───────┘
             │                │               ▼
             │                │        ┌──────────────┐
             │                │        │  food_agent  │
             │                │        └──────┬───────┘
             └───────┬────────┴───────────────┤
                     ▼                        ▼
             ┌────────────────────────────────────┐
             │            optimizer_agent         │
             └────────────────┬───────────────────┘
                              ▼
             ┌────────────────────────────────────┐
             │         final_synthesizer_node     │
             └────────────────┬───────────────────┘
                              ▼
                        (END - response)
```

---

## 🚀 Cài Đặt & Chạy

### Backend

```bash
# 1. Tạo môi trường ảo và cài dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Cấu hình biến môi trường
cp .env.example .env
# Điền OPENAI_API_KEY, SERPAPI_KEY, MAPBOX_ACCESS_TOKEN, SECRET_KEY vào .env

# 3. Chạy server (tự động tạo database SQLite tại ./data/app.db)
uvicorn main:app --reload --port 8000
```

Truy cập:
- API Docs (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Docker

```bash
docker build -t trip-planner .
docker run -p 8000:8000 --env-file .env trip-planner
```

### Frontend (tùy chọn)

```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 Biến Môi Trường

| Biến | Bắt buộc | Mô tả |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | API key OpenAI cho agent tổng hợp lịch trình |
| `SERPAPI_KEY` | ✅ | API key SerpApi (Google Flights / Hotels / Maps) |
| `MAPBOX_ACCESS_TOKEN` | ✅ | Token Mapbox cho ma trận khoảng cách |
| `SECRET_KEY` | ✅ | Khóa bí mật ký JWT (nên dùng chuỗi ngẫu nhiên dài) |
| `DATABASE_URL` | ❌ | Mặc định `sqlite+aiosqlite:///./data/app.db` |
| `CORS_ORIGINS` | ❌ | Danh sách origin được phép, phân tách bởi dấu phẩy |

---

## 📡 API Endpoints

### Auth (`/api/v1/auth`)
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/register` | Đăng ký tài khoản |
| POST | `/login` | Đăng nhập (OAuth2 form) — trả về access + refresh token |

### Planner (`/api/v1`)
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/plan-trip` | Tạo kế hoạch du lịch (yêu cầu Bearer token) — trả header `X-Trip-Id` |
| GET | `/trips` | Danh sách chuyến đi của user hiện tại |
| GET | `/trips/{trip_id}` | Chi tiết chuyến đi (chỉ chủ sở hữu) |
| DELETE | `/trips/{trip_id}` | Xóa chuyến đi (chỉ chủ sở hữu) |

### Config (`/api/v1`)
| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/tag_config` | Các tag/enum cho frontend render form |

Ví dụ tạo kế hoạch:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=you@example.com&password=secret123" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -s -X POST http://localhost:8000/api/v1/plan-trip \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "HAN",
    "destination": "SGN",
    "departure_date": "2026-12-01",
    "return_date": "2026-12-05",
    "max_budget": 1500,
    "num_adults": 2,
    "travel_pace": "balanced",
    "activity_categories": ["museum", "food"]
  }'
```

---

## 🧪 Chạy Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

Bộ test bao gồm: thuật toán TSP, tính chi phí, parser SerpApi, validation request, bảo mật JWT, cache service, TTL cache chuyến bay, giờ mở cửa, và integration tests cho toàn bộ API (auth + planner).

---

## 📁 Cấu Trúc Thư Mục

```text
main.py                     # Entry point FastAPI
app/
├── agents/
│   ├── graph.py            # LangGraph StateGraph pipeline
│   ├── state.py            # Agent state (TypedDict)
│   └── nodes/              # Các agent node
│       ├── extractor.py    # Trích xuất ý định & tính số ngày
│       ├── flight.py       # Tìm chuyến bay (Google Flights)
│       ├── hotel.py        # Tìm khách sạn (Google Hotels)
│       ├── activity.py     # Tìm điểm tham quan (Google Maps)
│       ├── cluster.py      # KMeans phân cụm theo ngày
│       ├── food.py         # Tìm nhà hàng quanh cụm
│       ├── optimizer.py    # Tối ưu chi phí + TSP
│       └── synthesizer.py  # Tổng hợp lịch trình markdown bằng LLM
├── api/v1/
│   ├── planner.py          # Routes plan-trip, trips CRUD
│   └── routers/            # auth, config
├── core/
│   ├── llm.py              # ChatOpenAI wrapper
│   └── security.py         # JWT + bcrypt
├── db/                     # SQLAlchemy models + async engine
├── schemas/                # Pydantic request/response
├── services/               # cache, db_service, mapbox, serpapi
└── utils/                  # cost_calculator, serpapi_parser, tsp
frontend/                   # Next.js UI
tests/                      # pytest suite
```

---

## 📄 Giấy Phép

MIT License - xem [LICENSE](LICENSE).
