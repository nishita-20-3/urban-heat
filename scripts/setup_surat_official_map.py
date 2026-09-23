import json
import math
from sqlalchemy import text
from app.database import engine, SessionLocal

# ==============================================================================
# SURAT MUNICIPAL CORPORATION (SMC) - 7 ADMINISTRATIVE PLANNING ZONES
# Curved, non-overlapping geomorphic boundaries matching the official SMC map
# ==============================================================================

SURAT_ZONES = [
    {
        "zone_id": 1,
        "name": "Central Zone",
        "code": "CZ-01",
        "description": "City North, City South, Begampura. Historic walled core, dense bazaar corridors, high thermal mass heritage structures.",
        "color": "#F59E0B",  # Peach/Warm Amber
        "polygon": [
            [72.808, 21.182], [72.804, 21.192], [72.808, 21.202], [72.818, 21.208],
            [72.828, 21.209], [72.838, 21.205], [72.842, 21.196], [72.839, 21.185],
            [72.828, 21.180], [72.818, 21.179], [72.808, 21.182]
        ]
    },
    {
        "zone_id": 2,
        "name": "North Zone (Katargam)",
        "code": "NZ-02",
        "description": "Singanpor, Katargam (Hotspot), Gayatri Depo, Amroli, Mota Varachha. Major diamond polishing clusters, dense residential wards, Kosad expansion.",
        "color": "#8B5CF6",  # Slate Purple/Grey outline
        "polygon": [
            [72.808, 21.202], [72.804, 21.218], [72.809, 21.238], [72.818, 21.252],
            [72.835, 21.265], [72.860, 21.268], [72.885, 21.258], [72.895, 21.242],
            [72.875, 21.228], [72.852, 21.220], [72.838, 21.205], [72.828, 21.209],
            [72.818, 21.208], [72.808, 21.202]
        ]
    },
    {
        "zone_id": 3,
        "name": "East Zone (Varachha)",
        "code": "EZ-03",
        "description": "Fulpada (Hotspot), Kapodra, Lambe Hanuman, Puna, Simada, Sarthana. Diamond trading hub, textile embroidery clusters, Sarthana nature park.",
        "color": "#3B82F6",  # Royal Blue
        "polygon": [
            [72.838, 21.205], [72.852, 21.220], [72.875, 21.228], [72.895, 21.242],
            [72.920, 21.238], [72.942, 21.225], [72.945, 21.205], [72.930, 21.192],
            [72.905, 21.190], [72.875, 21.192], [72.855, 21.195], [72.842, 21.196],
            [72.838, 21.205]
        ]
    },
    {
        "zone_id": 4,
        "name": "Limbayat Zone (South-East)",
        "code": "EZ-04",
        "description": "Umarwada, Limbayat (Hotspot), Godadara, Navagam Dindoli. Dense migrant housing settlements, textile logistics godowns, Dindoli lake catchment.",
        "color": "#06B6D4",  # Cyan/Teal
        "polygon": [
            [72.839, 21.185], [72.855, 21.195], [72.875, 21.192], [72.905, 21.190],
            [72.930, 21.192], [72.938, 21.175], [72.932, 21.155], [72.915, 21.145],
            [72.885, 21.146], [72.862, 21.152], [72.846, 21.165], [72.839, 21.185]
        ]
    },
    {
        "zone_id": 5,
        "name": "South Zone (Udhna)",
        "code": "SZ-05",
        "description": "Udhna, Pandesara (Hotspot), Vadod, Bhestan (Hotspot), Unn. Heavy chemical dyeing & printing industrial mills, railway logistics, thermal hotspot.",
        "color": "#EF4444",  # Red
        "polygon": [
            [72.818, 21.179], [72.828, 21.180], [72.839, 21.185], [72.846, 21.165],
            [72.862, 21.152], [72.885, 21.146], [72.890, 21.125], [72.878, 21.100],
            [72.855, 21.082], [72.835, 21.085], [72.820, 21.108], [72.814, 21.135],
            [72.812, 21.160], [72.818, 21.179]
        ]
    },
    {
        "zone_id": 6,
        "name": "South-West Zone (Athwa)",
        "code": "SWZ-06",
        "description": "Athwa (Hotspot), Panas, Althan Bhatar, Bamroli, Bharthana, Vesu, Gaviyer. Tapi promenade, institutional university hub, coastal Dumas green corridor.",
        "color": "#10B981",  # Emerald Green
        "polygon": [
            [72.808, 21.182], [72.818, 21.179], [72.812, 21.160], [72.814, 21.135],
            [72.820, 21.108], [72.805, 21.102], [72.785, 21.110], [72.760, 21.118],
            [72.742, 21.135], [72.748, 21.155], [72.765, 21.170], [72.788, 21.178],
            [72.808, 21.182]
        ]
    },
    {
        "zone_id": 7,
        "name": "West Zone (Rander)",
        "code": "WZ-07",
        "description": "Rander, Palanpur Gam, Adajan, Pal. Historic riverfront settlement, dense Adajan commercial avenues, Tapi western flood embankments.",
        "color": "#0EA5E9",  # Sky Blue
        "polygon": [
            [72.808, 21.182], [72.788, 21.178], [72.765, 21.170], [72.748, 21.155],
            [72.738, 21.175], [72.742, 21.202], [72.760, 21.225], [72.785, 21.232],
            [72.804, 21.218], [72.808, 21.202], [72.804, 21.192], [72.808, 21.182]
        ]
    }
]


# ==============================================================================
# SURAT 34 OFFICIAL PLANNING SUB-AREAS
# Smooth, curved geomorphic polygons with accurate physical land feasibility
# ==============================================================================

SURAT_AREAS_34 = [
    # ── Zone 1: Central Zone (Peach #F59E0B) ──
    {
        "area_id": 1,
        "zone_id": 1,
        "city_id": 1,
        "name": "City North",
        "code": "CZ-01",
        "area_type": "Historic Commercial Core",
        "is_hotspot": False,
        "description": "Chowk Bazaar, Surat Fort riverfront bend, Dutch Garden, heritage markets, narrow shaded street canyons.",
        "polygon": [
            [72.808, 21.195], [72.804, 21.202], [72.812, 21.206], [72.825, 21.208],
            [72.830, 21.202], [72.822, 21.196], [72.808, 21.195]
        ],
        "building_sqm": 42000, "road_sqm": 18000, "open_sqm": 6000, "water_sqm": 14000, "tree_sqm": 7200, "base_temp": 42.8
    },
    {
        "area_id": 2,
        "zone_id": 1,
        "city_id": 1,
        "name": "City South",
        "code": "CZ-02",
        "area_type": "Dense Commercial Bazaar & Walled Core",
        "is_hotspot": True,  # ⭐ Official Star Hotspot
        "description": "Muglisara, SMC Civic HQ, Zampa Bazaar, heavy vehicular canyon, high thermal mass brick/concrete terraces.",
        "polygon": [
            [72.808, 21.182], [72.808, 21.195], [72.822, 21.196], [72.830, 21.188],
            [72.825, 21.180], [72.815, 21.180], [72.808, 21.182]
        ],
        "building_sqm": 58000, "road_sqm": 24000, "open_sqm": 3500, "water_sqm": 0, "tree_sqm": 2800, "base_temp": 46.2
    },
    {
        "area_id": 3,
        "zone_id": 1,
        "city_id": 1,
        "name": "Begampura",
        "code": "CZ-03",
        "area_type": "Heritage Textile Weaving Hub",
        "is_hotspot": False,
        "description": "Begampura yarn market, traditional powerloom units, high building density, small open courtyards.",
        "polygon": [
            [72.822, 21.196], [72.830, 21.202], [72.838, 21.205], [72.842, 21.196],
            [72.839, 21.185], [72.830, 21.188], [72.822, 21.196]
        ],
        "building_sqm": 52000, "road_sqm": 22000, "open_sqm": 4500, "water_sqm": 0, "tree_sqm": 3100, "base_temp": 44.9
    },

    # ── Zone 2: North Zone (Purple/Grey #8B5CF6) ──
    {
        "area_id": 4,
        "zone_id": 2,
        "city_id": 1,
        "name": "Singanpor",
        "code": "NZ-01",
        "area_type": "Tapi Riverfront Residential Ward",
        "is_hotspot": False,
        "description": "Singanpor weir catchment, riverfront promenade, middle-income housing colonies, community parks.",
        "polygon": [
            [72.808, 21.202], [72.804, 21.218], [72.815, 21.225], [72.828, 21.222],
            [72.825, 21.208], [72.818, 21.208], [72.808, 21.202]
        ],
        "building_sqm": 45000, "road_sqm": 26000, "open_sqm": 19000, "water_sqm": 16000, "tree_sqm": 12500, "base_temp": 41.6
    },
    {
        "area_id": 5,
        "zone_id": 2,
        "city_id": 1,
        "name": "Katargam",
        "code": "NZ-02",
        "area_type": "Diamond Polishing & Industrial Hub",
        "is_hotspot": True,  # ⭐ Official Star Hotspot
        "description": "Katargam main diamond cutting/polishing clusters, GIDC units, metal sheet roofs, high anthropogenic heat.",
        "polygon": [
            [72.825, 21.208], [72.828, 21.222], [72.845, 21.225], [72.852, 21.220],
            [72.838, 21.205], [72.828, 21.209], [72.825, 21.208]
        ],
        "building_sqm": 86000, "road_sqm": 38000, "open_sqm": 4800, "water_sqm": 0, "tree_sqm": 3500, "base_temp": 47.6
    },
    {
        "area_id": 6,
        "zone_id": 2,
        "city_id": 1,
        "name": "Gayatri Depo",
        "code": "NZ-03",
        "area_type": "Transport Terminal & Commercial",
        "is_hotspot": False,
        "description": "BRTS transit junction, municipal bus depot, asphalt parking aprons, mixed low-rise retail.",
        "polygon": [
            [72.815, 21.225], [72.812, 21.238], [72.828, 21.242], [72.838, 21.232],
            [72.828, 21.222], [72.815, 21.225]
        ],
        "building_sqm": 32000, "road_sqm": 29000, "open_sqm": 12000, "water_sqm": 0, "tree_sqm": 4500, "base_temp": 44.1
    },
    {
        "area_id": 7,
        "zone_id": 2,
        "city_id": 1,
        "name": "Amroli",
        "code": "NZ-04",
        "area_type": "Northern Urban Expansion & Housing",
        "is_hotspot": False,
        "description": "Amroli bridge corridor, Kosad EWS housing township, large open land parcels, railway siding.",
        "polygon": [
            [72.809, 21.238], [72.818, 21.252], [72.842, 21.262], [72.855, 21.250],
            [72.838, 21.232], [72.828, 21.242], [72.812, 21.238], [72.809, 21.238]
        ],
        "building_sqm": 62000, "road_sqm": 35000, "open_sqm": 42000, "water_sqm": 8000, "tree_sqm": 11500, "base_temp": 43.4
    },
    {
        "area_id": 8,
        "zone_id": 2,
        "city_id": 1,
        "name": "Mota Varachha",
        "code": "NZ-05",
        "area_type": "Peri-Urban Township & Tapi Curve",
        "is_hotspot": False,
        "description": "Northern Tapi riverbank meander, planned high-rise residential towers, township gardens, agricultural fringes.",
        "polygon": [
            [72.842, 21.262], [72.860, 21.268], [72.885, 21.258], [72.895, 21.242],
            [72.875, 21.228], [72.855, 21.250], [72.842, 21.262]
        ],
        "building_sqm": 48000, "road_sqm": 28000, "open_sqm": 58000, "water_sqm": 18000, "tree_sqm": 16000, "base_temp": 40.5
    },

    # ── Zone 3: East Zone (Royal Blue #3B82F6) ──
    {
        "area_id": 9,
        "zone_id": 3,
        "city_id": 1,
        "name": "Fulpada",
        "code": "EZ-01",
        "area_type": "Dense Diamond & Textile Sector",
        "is_hotspot": True,  # ⭐ Official Star Hotspot
        "description": "Fulpada diamond manufacturing, heavy concrete building cover, narrow streets, low vegetative fraction.",
        "polygon": [
            [72.838, 21.205], [72.852, 21.220], [72.868, 21.218], [72.865, 21.202],
            [72.842, 21.196], [72.838, 21.205]
        ],
        "building_sqm": 79000, "road_sqm": 34000, "open_sqm": 3800, "water_sqm": 0, "tree_sqm": 2400, "base_temp": 47.8
    },
    {
        "area_id": 10,
        "zone_id": 3,
        "city_id": 1,
        "name": "Kapodra",
        "code": "EZ-02",
        "area_type": "Commercial Corridor & Societies",
        "is_hotspot": False,
        "description": "Varachha Main Road spine, diamond bourse trading offices, mid-rise residential apartments.",
        "polygon": [
            [72.868, 21.218], [72.875, 21.228], [72.895, 21.225], [72.890, 21.205],
            [72.865, 21.202], [72.868, 21.218]
        ],
        "building_sqm": 56000, "road_sqm": 29000, "open_sqm": 11000, "water_sqm": 0, "tree_sqm": 6200, "base_temp": 44.8
    },
    {
        "area_id": 11,
        "zone_id": 3,
        "city_id": 1,
        "name": "Lambe Hanuman",
        "code": "EZ-03",
        "area_type": "Mixed Residential & Retail Spine",
        "is_hotspot": False,
        "description": "Lambe Hanuman Road arterial corridor, dense residential societies, school grounds, market areas.",
        "polygon": [
            [72.842, 21.196], [72.865, 21.202], [72.875, 21.192], [72.855, 21.195],
            [72.842, 21.196]
        ],
        "building_sqm": 48000, "road_sqm": 22000, "open_sqm": 8500, "water_sqm": 0, "tree_sqm": 4800, "base_temp": 43.9
    },
    {
        "area_id": 12,
        "zone_id": 3,
        "city_id": 1,
        "name": "Puna",
        "code": "EZ-04",
        "area_type": "Textile Logistics & Housing Hub",
        "is_hotspot": False,
        "description": "Puna-Kumbharia textile market access, freight corridors, worker residential complexes.",
        "polygon": [
            [72.865, 21.202], [72.890, 21.205], [72.905, 21.190], [72.875, 21.192],
            [72.865, 21.202]
        ],
        "building_sqm": 64000, "road_sqm": 32000, "open_sqm": 12500, "water_sqm": 0, "tree_sqm": 5100, "base_temp": 45.3
    },
    {
        "area_id": 13,
        "zone_id": 3,
        "city_id": 1,
        "name": "Simada",
        "code": "EZ-05",
        "area_type": "Eastern Suburban Township Sector",
        "is_hotspot": False,
        "description": "Canal road corridor, planned high-rise gated communities, open institutional grounds.",
        "polygon": [
            [72.895, 21.225], [72.920, 21.238], [72.932, 21.218], [72.905, 21.190],
            [72.890, 21.205], [72.895, 21.225]
        ],
        "building_sqm": 46000, "road_sqm": 27000, "open_sqm": 38000, "water_sqm": 6000, "tree_sqm": 9500, "base_temp": 42.1
    },
    {
        "area_id": 14,
        "zone_id": 3,
        "city_id": 1,
        "name": "Sarthana",
        "code": "EZ-06",
        "area_type": "Nature Park & Urban Green Verge",
        "is_hotspot": False,
        "description": "Sarthana Nature Park, Tapi river intake water works, zoo botanical canopy, Valak creek buffer.",
        "polygon": [
            [72.895, 21.242], [72.920, 21.238], [72.942, 21.225], [72.945, 21.205],
            [72.930, 21.192], [72.932, 21.218], [72.895, 21.242]
        ],
        "building_sqm": 31000, "road_sqm": 19000, "open_sqm": 64000, "water_sqm": 26000, "tree_sqm": 38000, "base_temp": 39.2
    },

    # ── Zone 4: Limbayat Zone (Cyan #06B6D4) ──
    {
        "area_id": 15,
        "zone_id": 4,
        "city_id": 1,
        "name": "Umarwada",
        "code": "EZ-04A",
        "area_type": "Railway Logistics & Wholesale Market",
        "is_hotspot": False,
        "description": "Surat textile market ring road fringe, rail freight siding, transport warehouses.",
        "polygon": [
            [72.839, 21.185], [72.855, 21.195], [72.870, 21.185], [72.852, 21.172],
            [72.839, 21.185]
        ],
        "building_sqm": 58000, "road_sqm": 31000, "open_sqm": 6200, "water_sqm": 0, "tree_sqm": 3400, "base_temp": 45.6
    },
    {
        "area_id": 16,
        "zone_id": 4,
        "city_id": 1,
        "name": "Limbayat",
        "code": "EZ-04B",
        "area_type": "High-Density Worker Housing Colony",
        "is_hotspot": True,  # ⭐ Official Star Hotspot
        "description": "Ultra-dense residential tenements, tin/asbestos roofs, narrow unshaded alleys, extreme thermal retention.",
        "polygon": [
            [72.852, 21.172], [72.870, 21.185], [72.885, 21.178], [72.872, 21.160],
            [72.846, 21.165], [72.852, 21.172]
        ],
        "building_sqm": 88000, "road_sqm": 36000, "open_sqm": 4200, "water_sqm": 0, "tree_sqm": 2200, "base_temp": 48.2
    },
    {
        "area_id": 17,
        "zone_id": 4,
        "city_id": 1,
        "name": "Godadara",
        "code": "EZ-04C",
        "area_type": "Mixed Residential & Weaving Sector",
        "is_hotspot": False,
        "description": "Godadara canal road, small-scale embroidery units, mid-density residential societies.",
        "polygon": [
            [72.870, 21.185], [72.905, 21.190], [72.915, 21.175], [72.885, 21.178],
            [72.870, 21.185]
        ],
        "building_sqm": 54000, "road_sqm": 26000, "open_sqm": 16000, "water_sqm": 0, "tree_sqm": 5500, "base_temp": 44.5
    },
    {
        "area_id": 18,
        "zone_id": 4,
        "city_id": 1,
        "name": "Navagam Dindoli",
        "code": "EZ-04D",
        "area_type": "Suburban Township & Dindoli Lake Basin",
        "is_hotspot": False,
        "description": "Dindoli lake catchment, planned residential townships, school playgrounds, wide road network.",
        "polygon": [
            [72.872, 21.160], [72.885, 21.178], [72.915, 21.175], [72.930, 21.192],
            [72.938, 21.175], [72.932, 21.155], [72.915, 21.145], [72.885, 21.146],
            [72.862, 21.152], [72.872, 21.160]
        ],
        "building_sqm": 46000, "road_sqm": 25000, "open_sqm": 34000, "water_sqm": 14000, "tree_sqm": 11000, "base_temp": 42.6
    },

    # ── Zone 5: South Zone (Red #EF4444) ──
    {
        "area_id": 19,
        "zone_id": 5,
        "city_id": 1,
        "name": "Udhna",
        "code": "SZ-01",
        "area_type": "Railway Junction & Commercial Corridor",
        "is_hotspot": False,
        "description": "Udhna railway freight junction, metal market, heavy vehicle commercial corridors, transit spine.",
        "polygon": [
            [72.818, 21.179], [72.828, 21.180], [72.839, 21.185], [72.846, 21.165],
            [72.835, 21.155], [72.815, 21.160], [72.818, 21.179]
        ],
        "building_sqm": 56000, "road_sqm": 38000, "open_sqm": 8500, "water_sqm": 0, "tree_sqm": 4800, "base_temp": 45.8
    },
    {
        "area_id": 20,
        "zone_id": 5,
        "city_id": 1,
        "name": "Pandesara",
        "code": "SZ-02",
        "area_type": "Heavy Chemical Dyeing GIDC Industrial Estate",
        "is_hotspot": True,  # ⭐ Official Star Hotspot
        "description": "Pandesara GIDC heavy textile dyeing and chemical printing mills, metal roof sheds, severe heat emissions.",
        "polygon": [
            [72.812, 21.160], [72.815, 21.160], [72.835, 21.155], [72.842, 21.138],
            [72.825, 21.135], [72.814, 21.135], [72.812, 21.160]
        ],
        "building_sqm": 92000, "road_sqm": 44000, "open_sqm": 3500, "water_sqm": 0, "tree_sqm": 1800, "base_temp": 48.9
    },
    {
        "area_id": 21,
        "zone_id": 5,
        "city_id": 1,
        "name": "Vadod",
        "code": "SZ-03",
        "area_type": "Mixed Industrial & Residential Ward",
        "is_hotspot": False,
        "description": "Textile auxiliary units, worker housing societies, unpaved open soil plots, canal margins.",
        "polygon": [
            [72.835, 21.155], [72.846, 21.165], [72.862, 21.152], [72.855, 21.135],
            [72.842, 21.138], [72.835, 21.155]
        ],
        "building_sqm": 48000, "road_sqm": 24000, "open_sqm": 22000, "water_sqm": 0, "tree_sqm": 6500, "base_temp": 44.8
    },
    {
        "area_id": 22,
        "zone_id": 5,
        "city_id": 1,
        "name": "Bhestan",
        "code": "SZ-04",
        "area_type": "Industrial Peripheral & Freight Hub",
        "is_hotspot": True,  # ⭐ Official Star Hotspot
        "description": "Bhestan railway freight yard, municipal housing quarters, large unshaded asphalt freight bays.",
        "polygon": [
            [72.842, 21.138], [72.855, 21.135], [72.862, 21.152], [72.885, 21.146],
            [72.890, 21.125], [72.865, 21.118], [72.842, 21.138]
        ],
        "building_sqm": 68000, "road_sqm": 36000, "open_sqm": 14000, "water_sqm": 0, "tree_sqm": 3800, "base_temp": 47.9
    },
    {
        "area_id": 23,
        "zone_id": 5,
        "city_id": 1,
        "name": "Unn",
        "code": "SZ-05",
        "area_type": "Southern Suburban & Industrial Fringe",
        "is_hotspot": False,
        "description": "Southern municipal limits, textile labour colonies, open agricultural conversion land.",
        "polygon": [
            [72.814, 21.135], [72.825, 21.135], [72.842, 21.138], [72.865, 21.118],
            [72.878, 21.100], [72.855, 21.082], [72.835, 21.085], [72.820, 21.108],
            [72.814, 21.135]
        ],
        "building_sqm": 40000, "road_sqm": 22000, "open_sqm": 48000, "water_sqm": 0, "tree_sqm": 8500, "base_temp": 43.8
    },

    # ── Zone 6: South-West Zone (Emerald Green #10B981) ──
    {
        "area_id": 24,
        "zone_id": 6,
        "city_id": 1,
        "name": "Athwa",
        "code": "SWZ-01",
        "area_type": "Riverfront & Government Boulevard",
        "is_hotspot": True,  # ⭐ Official Star Hotspot
        "description": "Athwa lines government quarters, court complexes, Tapi riverfront promenade, wide asphalt boulevards.",
        "polygon": [
            [72.788, 21.178], [72.808, 21.182], [72.818, 21.179], [72.810, 21.165],
            [72.795, 21.162], [72.788, 21.178]
        ],
        "building_sqm": 42000, "road_sqm": 32000, "open_sqm": 18000, "water_sqm": 12000, "tree_sqm": 18000, "base_temp": 44.8
    },
    {
        "area_id": 25,
        "zone_id": 6,
        "city_id": 1,
        "name": "Panas",
        "code": "SWZ-02",
        "area_type": "Riverbank Residential Ward",
        "is_hotspot": False,
        "description": "Tapi riverbank residential societies, low-rise bungalows, municipal recreational parks.",
        "polygon": [
            [72.765, 21.170], [72.788, 21.178], [72.795, 21.162], [72.775, 21.155],
            [72.765, 21.170]
        ],
        "building_sqm": 38000, "road_sqm": 22000, "open_sqm": 24000, "water_sqm": 8000, "tree_sqm": 16000, "base_temp": 41.5
    },
    {
        "area_id": 26,
        "zone_id": 6,
        "city_id": 1,
        "name": "Althan Bhatar",
        "code": "SWZ-03",
        "area_type": "Prime Commercial & Residential Center",
        "is_hotspot": False,
        "description": "VIP Road commercial malls, high-rise residential societies, canal corridor green verge.",
        "polygon": [
            [72.795, 21.162], [72.808, 21.165], [72.812, 21.148], [72.792, 21.145],
            [72.795, 21.162]
        ],
        "building_sqm": 58000, "road_sqm": 30000, "open_sqm": 14000, "water_sqm": 0, "tree_sqm": 9000, "base_temp": 43.8
    },
    {
        "area_id": 27,
        "zone_id": 6,
        "city_id": 1,
        "name": "Bamroli",
        "code": "SWZ-04",
        "area_type": "Institutional & Mixed Residential Ward",
        "is_hotspot": False,
        "description": "Bamroli industrial road fringe, low-income housing societies, open municipal school grounds.",
        "polygon": [
            [72.792, 21.145], [72.812, 21.148], [72.814, 21.135], [72.820, 21.108],
            [72.805, 21.102], [72.792, 21.125], [72.792, 21.145]
        ],
        "building_sqm": 44000, "road_sqm": 26000, "open_sqm": 28000, "water_sqm": 0, "tree_sqm": 7500, "base_temp": 44.2
    },
    {
        "area_id": 28,
        "zone_id": 6,
        "city_id": 1,
        "name": "Bharthana",
        "code": "SWZ-05",
        "area_type": "University & Institutional Campus Sector",
        "is_hotspot": False,
        "description": "VNSGU South Gujarat University campus, botanical gardens, institutional tree canopy.",
        "polygon": [
            [72.775, 21.155], [72.795, 21.162], [72.792, 21.145], [72.792, 21.125],
            [72.768, 21.135], [72.775, 21.155]
        ],
        "building_sqm": 34000, "road_sqm": 24000, "open_sqm": 46000, "water_sqm": 0, "tree_sqm": 26000, "base_temp": 40.8
    },
    {
        "area_id": 29,
        "zone_id": 6,
        "city_id": 1,
        "name": "Vesu",
        "code": "SWZ-06",
        "area_type": "Modern Township & Institutional Boulevard",
        "is_hotspot": False,
        "description": "SVNIT corridor, luxury residential high-rises, wide avenue plantations, university sports grounds.",
        "polygon": [
            [72.748, 21.155], [72.765, 21.170], [72.775, 21.155], [72.768, 21.135],
            [72.742, 21.135], [72.748, 21.155]
        ],
        "building_sqm": 52000, "road_sqm": 34000, "open_sqm": 38000, "water_sqm": 0, "tree_sqm": 19000, "base_temp": 41.8
    },
    {
        "area_id": 30,
        "zone_id": 6,
        "city_id": 1,
        "name": "Gaviyer",
        "code": "SWZ-07",
        "area_type": "Coastal Airport & Wetland Buffer",
        "is_hotspot": False,
        "description": "Surat International Airport runway buffer, Dumas coastal creek, mangrove estuaries, open saline soil.",
        "polygon": [
            [72.742, 21.135], [72.768, 21.135], [72.792, 21.125], [72.805, 21.102],
            [72.785, 21.110], [72.760, 21.118], [72.742, 21.135]
        ],
        "building_sqm": 28000, "road_sqm": 32000, "open_sqm": 86000, "water_sqm": 32000, "tree_sqm": 24000, "base_temp": 39.4
    },

    # ── Zone 7: West Zone (Sky Blue #0EA5E9) ──
    {
        "area_id": 31,
        "zone_id": 7,
        "city_id": 1,
        "name": "Rander",
        "code": "WZ-01",
        "area_type": "Historic Riverfront Heritage Town",
        "is_hotspot": False,
        "description": "Historic Rander town, ancient mosque quarters, dense traditional timber/brick houses, riverbank steps.",
        "polygon": [
            [72.785, 21.218], [72.804, 21.218], [72.808, 21.202], [72.804, 21.192],
            [72.785, 21.198], [72.785, 21.218]
        ],
        "building_sqm": 49000, "road_sqm": 21000, "open_sqm": 9000, "water_sqm": 12000, "tree_sqm": 8500, "base_temp": 42.4
    },
    {
        "area_id": 32,
        "zone_id": 7,
        "city_id": 1,
        "name": "Palanpur Gam",
        "code": "WZ-02",
        "area_type": "North-Western Suburban Township",
        "is_hotspot": False,
        "description": "Palanpur canal road, Gavier lake approach, residential high-rises, canal park corridor.",
        "polygon": [
            [72.760, 21.225], [72.785, 21.232], [72.785, 21.218], [72.765, 21.202],
            [72.742, 21.202], [72.760, 21.225]
        ],
        "building_sqm": 44000, "road_sqm": 26000, "open_sqm": 32000, "water_sqm": 6000, "tree_sqm": 12000, "base_temp": 41.2
    },
    {
        "area_id": 33,
        "zone_id": 7,
        "city_id": 1,
        "name": "Adajan",
        "code": "WZ-03",
        "area_type": "Prime Commercial & Residential Center",
        "is_hotspot": False,
        "description": "Adajan Patiya, Prime Arcade, LP Savani Road, high-density residential apartments, commercial arcades.",
        "polygon": [
            [72.765, 21.202], [72.785, 21.218], [72.785, 21.198], [72.804, 21.192],
            [72.808, 21.182], [72.788, 21.178], [72.765, 21.185], [72.765, 21.202]
        ],
        "building_sqm": 62000, "road_sqm": 34000, "open_sqm": 18000, "water_sqm": 0, "tree_sqm": 14000, "base_temp": 43.1
    },
    {
        "area_id": 34,
        "zone_id": 7,
        "city_id": 1,
        "name": "Pal",
        "code": "WZ-04",
        "area_type": "Suburban Riverfront & Botanical Parks",
        "is_hotspot": False,
        "description": "Pal RTO, Pal Botanical Garden, Tapi western promenade, low-density modern housing societies.",
        "polygon": [
            [72.738, 21.175], [72.765, 21.185], [72.788, 21.178], [72.765, 21.170],
            [72.748, 21.155], [72.738, 21.175]
        ],
        "building_sqm": 36000, "road_sqm": 22000, "open_sqm": 42000, "water_sqm": 16000, "tree_sqm": 22000, "base_temp": 39.8
    }
]


def setup_surat_map():
    db = SessionLocal()
    try:
        print("1. Adding is_hotspot column to planning_areas if needed...")
        db.execute(text("""
            ALTER TABLE planning_areas ADD COLUMN IF NOT EXISTS is_hotspot BOOLEAN DEFAULT FALSE;
        """))
        db.commit()

        print("2. Updating 7 SMC Zones with map-accurate curved boundaries and colors...")
        for z in SURAT_ZONES:
            poly_coords = z["polygon"]
            wkt_coords = ", ".join([f"{coord[0]} {coord[1]}" for coord in poly_coords])
            wkt = f"MULTIPOLYGON((({wkt_coords})))"

            db.execute(text("""
                INSERT INTO zones (zone_id, city_id, name, code, description, color, geom)
                VALUES (:zid, 1, :name, :code, :desc, :color, ST_Multi(ST_GeomFromText(:wkt, 4326)))
                ON CONFLICT (zone_id) DO UPDATE 
                SET name = EXCLUDED.name, 
                    code = EXCLUDED.code, 
                    description = EXCLUDED.description, 
                    color = EXCLUDED.color,
                    geom = EXCLUDED.geom;
            """), {
                "zid": z["zone_id"],
                "name": z["name"],
                "code": z["code"],
                "desc": z["description"],
                "color": z["color"],
                "wkt": wkt
            })
        db.commit()

        print("3. Populating all 34 Official Surat Sub-Areas from map...")
        # Ensure Ahmedabad areas with ids <= 100 are cleanly shifted to 200+
        db.execute(text("""
            ALTER TABLE grid_cells DROP CONSTRAINT IF EXISTS grid_cells_area_id_fkey;
            UPDATE planning_areas SET area_id = area_id + 200 WHERE city_id = 2 AND area_id < 200;
            UPDATE grid_cells SET area_id = area_id + 200 WHERE city_id = 2 AND area_id IS NOT NULL AND area_id < 200;
            DELETE FROM planning_areas WHERE city_id = 1;
        """))
        db.commit()

        for a in SURAT_AREAS_34:
            poly_coords = a["polygon"]
            wkt_coords = ", ".join([f"{coord[0]} {coord[1]}" for coord in poly_coords])
            wkt = f"MULTIPOLYGON((({wkt_coords})))"

            db.execute(text("""
                INSERT INTO planning_areas (
                    area_id, zone_id, city_id, name, code, area_type, is_hotspot, description,
                    building_rooftop_sqm, road_paved_sqm, open_ground_sqm, water_body_sqm, existing_tree_cover_sqm,
                    avg_lst_summer, peak_lst_summer, geom
                )
                VALUES (
                    :aid, :zid, :cid, :name, :code, :atype, :hotspot, :desc,
                    :bsqm, :rsqm, :osqm, :wsqm, :tsqm,
                    :avg_t, :peak_t, ST_Multi(ST_GeomFromText(:wkt, 4326))
                )
                ON CONFLICT (area_id) DO UPDATE
                SET zone_id = EXCLUDED.zone_id,
                    city_id = EXCLUDED.city_id,
                    name = EXCLUDED.name,
                    code = EXCLUDED.code,
                    area_type = EXCLUDED.area_type,
                    is_hotspot = EXCLUDED.is_hotspot,
                    description = EXCLUDED.description,
                    building_rooftop_sqm = EXCLUDED.building_rooftop_sqm,
                    road_paved_sqm = EXCLUDED.road_paved_sqm,
                    open_ground_sqm = EXCLUDED.open_ground_sqm,
                    water_body_sqm = EXCLUDED.water_body_sqm,
                    existing_tree_cover_sqm = EXCLUDED.existing_tree_cover_sqm,
                    avg_lst_summer = EXCLUDED.avg_lst_summer,
                    peak_lst_summer = EXCLUDED.peak_lst_summer,
                    geom = EXCLUDED.geom;
            """), {
                "aid": a["area_id"],
                "zid": a["zone_id"],
                "cid": a["city_id"],
                "name": a["name"],
                "code": a["code"],
                "atype": a["area_type"],
                "hotspot": a["is_hotspot"],
                "desc": a["description"],
                "bsqm": a["building_sqm"],
                "rsqm": a["road_sqm"],
                "osqm": a["open_sqm"],
                "wsqm": a["water_sqm"],
                "tsqm": a["tree_sqm"],
                "avg_t": a["base_temp"],
                "peak_t": round(a["base_temp"] + 2.8, 1),
                "wkt": wkt
            })
        db.commit()

        # Re-add foreign key constraint
        db.execute(text("""
            ALTER TABLE grid_cells ADD CONSTRAINT grid_cells_area_id_fkey FOREIGN KEY (area_id) REFERENCES planning_areas(area_id);
        """))
        db.commit()

        print("4. Re-linking Surat grid cells spatially to zones and planning areas...")
        db.execute(text("""
            UPDATE grid_cells gc
            SET zone_id = z.zone_id
            FROM zones z
            WHERE gc.city_id = z.city_id
              AND ST_Intersects(gc.centroid, z.geom);
        """))
        db.commit()

        db.execute(text("""
            UPDATE grid_cells gc
            SET area_id = pa.area_id
            FROM planning_areas pa
            WHERE gc.city_id = pa.city_id
              AND ST_Intersects(gc.centroid, pa.geom);
        """))
        db.commit()

        counts = db.execute(text("""
            SELECT z.name as zone_name, pa.area_id, pa.name as area_name, pa.is_hotspot, count(gc.cell_id) as cell_count
            FROM planning_areas pa
            JOIN zones z ON z.zone_id = pa.zone_id
            LEFT JOIN grid_cells gc ON gc.area_id = pa.area_id
            WHERE pa.city_id = 1
            GROUP BY z.name, pa.area_id, pa.name, pa.is_hotspot
            ORDER BY pa.area_id;
        """)).fetchall()

        print("\nAll 34 Official Surat Planning Areas Successfully Configured with Curved Geomorphic Boundaries:")
        for r in counts:
            hotspot_tag = " [STAR HOTSPOT]" if r[3] else ""
            print(f"  [{r[0]}] Area #{r[1]}: {r[2]}{hotspot_tag} -> {r[4]:,} cells mapped")

    finally:
        db.close()


if __name__ == "__main__":
    setup_surat_map()
