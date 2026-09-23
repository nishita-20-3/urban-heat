# 🏙️ Urban Heat Decision-Support System (UHDSS)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6+-3178C6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.0+-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://postgis.net/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-38B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An advanced, full-stack **Urban Heat Island (UHI) Decision-Support System** designed for Indian Municipal Corporations and urban local bodies. Built with a high-performance **FastAPI + PostGIS** geospatial engine and a modern **React + Vite + Leaflet** interactive interface, it delivers 100m-resolution thermal microclimate forecasting, SHAP explainability, and area-wise physical land feasibility planning.

---

## 🌟 Key Capabilities

1. **3-Tier Simultaneous Geospatial Hierarchy**:
   - **Top Tier (Municipal Zones)**: 7 administrative planning zones with official perimeter outlines and signature zone colors.
   - **Middle Tier (Planning Sub-Areas)**: 34 official planning sub-areas featuring smooth, curved geomorphic boundaries adhering to natural river meanders, coastal estuaries, and ring roads, with official **Star Hotspot ⭐** markers.
   - **Base Tier (100m Microclimate Heat Grid)**: High-resolution raster cells with calibrated thermal color scaling (34°C to 54°C).

2. **Machine Learning & SHAP Explainability**:
   - Seasonal Land Surface Temperature (LST) predictions across Summer, Monsoon, Post-Monsoon, and Winter.
   - Per-cell Tree SHAP explainability attributing thermal anomalies to surface albedo, NDVI vegetation index, built-up fraction, road density, and moisture availability.

3. **Area-Wise Physical Land Feasibility Packages**:
   - Practical, municipal-grade intervention budgets formulated by physical surface classification:
     - 🏢 **Building Rooftops (m²)** $\rightarrow$ High-albedo Cool Roofs & Solar-Reflective Coatings.
     - 🛣️ **Road & Paved Corridors (m²)** $\rightarrow$ Arterial Avenue Shade Trees & Permeable Margins.
     - 🌳 **Open Ground Parcels (m²)** $\rightarrow$ Miyawaki High-Density Urban Forests & Micro-Parks.
     - 💧 **Water & Creek Buffers (m²)** $\rightarrow$ Riparian Wetland Buffers & Creek Aeration.

4. **Multi-City Support**:
   - Built-in multi-city spatial schema supporting Surat (Primary Prototype) and Ahmedabad.

---

## 🏗️ Architecture

```
urban-heat-system/
├── app/                        # FastAPI Backend Application
│   ├── main.py                 # Application entry point & middleware
│   ├── config.py               # Pydantic v2 settings & database config
│   ├── database.py             # SQLAlchemy 2.0 engine & connection pooling
│   ├── models/                 # SQLAlchemy & GeoAlchemy2 PostGIS models
│   ├── schemas/                # Pydantic request/response validation
│   ├── services/               # Core business, spatial & ML services
│   └── routers/                # REST API endpoints (zones, areas, grid, SHAP)
├── frontend/                   # React 19 + Vite + TypeScript Frontend
│   ├── src/
│   │   ├── components/map/     # Leaflet HeatMap, 3-Tier Layering, Controls, Legend
│   │   ├── components/drawer/  # Zone, Area, and Cell Detail slide-out drawers
│   │   ├── hooks/              # Data fetching, debounce & viewport sync hooks
│   │   └── utils/              # Color scales, formatters, and metadata
├── scripts/                    # Database seeding & spatial population scripts
├── tests/                      # Automated Pytest suite
└── requirements.txt            # Python dependencies
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`
- **PostgreSQL 14+** with the **PostGIS** extension enabled

---

### 1. Backend Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/intelligent-carson.git
   cd intelligent-carson
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and set your PostgreSQL PostGIS connection string:
   ```bash
   cp .env.example .env
   ```
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/urban_heat_db
   ```

5. **Populate PostGIS Spatial Boundaries & Data**:
   ```bash
   python -m scripts.setup_surat_official_map
   ```

6. **Start the FastAPI Development Server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`
   - **Alternative Docs (ReDoc)**: `http://localhost:8000/redoc`

---

### 2. Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   - Open `http://localhost:5173` in your browser.

4. **Build for Production**:
   ```bash
   npm run build
   ```

---

## 🧪 Testing

Run the automated backend test suite:
```bash
python -m pytest tests/
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
