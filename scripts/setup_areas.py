import os
import json
import random
from sqlalchemy import text
from app.database import engine, SessionLocal

# 21 Official / Practical Neighborhood Planning Areas of Surat Municipal Corporation
# 3 Planning Areas inside each of the 7 Zones
SURAT_AREAS = [
    # ── Zone 1: Central Zone (CZ-01) ──
    {
        "area_id": 1,
        "zone_id": 1,
        "city_id": 1,
        "name": "Chowk Bazaar & Heritage Walled Core",
        "code": "CZ-A01",
        "area_type": "Dense Commercial Heritage",
        "description": "Dense historic bazaar, Fort road, narrow street canyons with zero setbacks and high thermal mass.",
        "polygon": [
            [72.805, 21.185],
            [72.822, 21.185],
            [72.825, 21.198],
            [72.808, 21.198],
            [72.805, 21.185]
        ],
        "building_sqm": 42000,
        "road_sqm": 22000,
        "open_sqm": 4500,
        "water_sqm": 2000,
        "tree_sqm": 3500,
        "base_temp": 46.8
    },
    {
        "area_id": 2,
        "zone_id": 1,
        "city_id": 1,
        "name": "Muglisara & SMC Civic Headquarters",
        "code": "CZ-A02",
        "area_type": "Civic & Administrative Core",
        "description": "Administrative municipal offices, civic plazas, high pedestrian density and paved parking lots.",
        "polygon": [
            [72.822, 21.185],
            [72.838, 21.185],
            [72.840, 21.198],
            [72.825, 21.198],
            [72.822, 21.185]
        ],
        "building_sqm": 38000,
        "road_sqm": 26000,
        "open_sqm": 8000,
        "water_sqm": 0,
        "tree_sqm": 5000,
        "base_temp": 45.9
    },
    {
        "area_id": 3,
        "zone_id": 1,
        "city_id": 1,
        "name": "Nanpura & Dutch Garden Riverside",
        "code": "CZ-A03",
        "area_type": "Mixed Residential & Riverfront",
        "description": "Historic colonial residential sector, botanical gardens, and Tapi river edge promenade.",
        "polygon": [
            [72.808, 21.198],
            [72.825, 21.198],
            [72.836, 21.208],
            [72.820, 21.212],
            [72.808, 21.202],
            [72.808, 21.198]
        ],
        "building_sqm": 32000,
        "road_sqm": 18000,
        "open_sqm": 12000,
        "water_sqm": 8000,
        "tree_sqm": 14000,
        "base_temp": 43.5
    },

    # ── Zone 2: North Zone - Katargam (NZ-02) ──
    {
        "area_id": 4,
        "zone_id": 2,
        "city_id": 1,
        "name": "Katargam Diamond Bourse Industrial Hub",
        "code": "NZ-A01",
        "area_type": "Industrial Diamond Cutting",
        "description": "High-density diamond polishing workshops, metal/concrete shed roofs, intense heat emissions.",
        "polygon": [
            [72.808, 21.202],
            [72.836, 21.208],
            [72.855, 21.225],
            [72.830, 21.235],
            [72.808, 21.202]
        ],
        "building_sqm": 65000,
        "road_sqm": 30000,
        "open_sqm": 8500,
        "water_sqm": 0,
        "tree_sqm": 4200,
        "base_temp": 47.2
    },
    {
        "area_id": 5,
        "zone_id": 2,
        "city_id": 1,
        "name": "Singanpore & Gotalawadi Residential Ward",
        "code": "NZ-A02",
        "area_type": "High-Density Residential",
        "description": "Dense middle-income housing societies, commercial arterial corridors with limited canopy cover.",
        "polygon": [
            [72.830, 21.235],
            [72.855, 21.225],
            [72.868, 21.250],
            [72.845, 21.255],
            [72.830, 21.235]
        ],
        "building_sqm": 52000,
        "road_sqm": 25000,
        "open_sqm": 14000,
        "water_sqm": 0,
        "tree_sqm": 9000,
        "base_temp": 45.4
    },
    {
        "area_id": 6,
        "zone_id": 2,
        "city_id": 1,
        "name": "Amroli & Kosad Urban Expansion Area",
        "code": "NZ-A03",
        "area_type": "Suburban & Housing Board",
        "description": "Municipal housing schemes, open agricultural conversion plots, broad arterial roads.",
        "polygon": [
            [72.795, 21.245],
            [72.830, 21.235],
            [72.845, 21.255],
            [72.850, 21.270],
            [72.820, 21.265],
            [72.795, 21.245]
        ],
        "building_sqm": 38000,
        "road_sqm": 22000,
        "open_sqm": 35000,
        "water_sqm": 4000,
        "tree_sqm": 12000,
        "base_temp": 44.1
    },

    # ── Zone 3: East Zone-A - Varachha (EZ-03) ──
    {
        "area_id": 7,
        "zone_id": 3,
        "city_id": 1,
        "name": "Varachha Main Commercial Diamond Corridor",
        "code": "EZ-A01",
        "area_type": "Commercial Trading Hub",
        "description": "Dense diamond trading bazaars, flyovers, heavy continuous traffic, paved parking lots.",
        "polygon": [
            [72.836, 21.208],
            [72.875, 21.198],
            [72.885, 21.220],
            [72.855, 21.225],
            [72.836, 21.208]
        ],
        "building_sqm": 58000,
        "road_sqm": 35000,
        "open_sqm": 6000,
        "water_sqm": 0,
        "tree_sqm": 4500,
        "base_temp": 47.5
    },
    {
        "area_id": 8,
        "zone_id": 3,
        "city_id": 1,
        "name": "Nana Varachha & Kapodra Sector",
        "code": "EZ-A02",
        "area_type": "Mixed Residential & Industrial",
        "description": "Textile embroidery units, dense housing societies, concrete roofs and unshaded street verges.",
        "polygon": [
            [72.855, 21.225],
            [72.885, 21.220],
            [72.905, 21.215],
            [72.900, 21.240],
            [72.855, 21.225]
        ],
        "building_sqm": 62000,
        "road_sqm": 28000,
        "open_sqm": 11000,
        "water_sqm": 0,
        "tree_sqm": 6000,
        "base_temp": 46.7
    },
    {
        "area_id": 9,
        "zone_id": 3,
        "city_id": 1,
        "name": "Sarthana Nature Park & Urban Green Verge",
        "code": "EZ-A03",
        "area_type": "Ecological & Urban Fringe",
        "description": "Sarthana Nature Park, zoo buffer zones, canal corridors, moderate tree canopy.",
        "polygon": [
            [72.885, 21.220],
            [72.900, 21.240],
            [72.915, 21.245],
            [72.885, 21.255],
            [72.885, 21.220]
        ],
        "building_sqm": 25000,
        "road_sqm": 18000,
        "open_sqm": 42000,
        "water_sqm": 6500,
        "tree_sqm": 28000,
        "base_temp": 42.8
    },

    # ── Zone 4: East Zone-B - Limbayat (EZ-04) ──
    {
        "area_id": 10,
        "zone_id": 4,
        "city_id": 1,
        "name": "Limbayat High-Density Housing Colony",
        "code": "EZ-B01",
        "area_type": "Vulnerable Dense Settlement",
        "description": "High-density migrant housing colonies, tin/asbestos sheets, narrow lanes with severe heat vulnerability.",
        "polygon": [
            [72.838, 21.185],
            [72.875, 21.198],
            [72.885, 21.175],
            [72.845, 21.165],
            [72.838, 21.185]
        ],
        "building_sqm": 72000,
        "road_sqm": 24000,
        "open_sqm": 5000,
        "water_sqm": 0,
        "tree_sqm": 2800,
        "base_temp": 48.1
    },
    {
        "area_id": 11,
        "zone_id": 4,
        "city_id": 1,
        "name": "Godadara & Parvat Patiya Sector",
        "code": "EZ-B02",
        "area_type": "Textile Transit & Residential",
        "description": "Textile processing godowns, logistics parking, dense multistory residential apartments.",
        "polygon": [
            [72.875, 21.198],
            [72.905, 21.215],
            [72.920, 21.180],
            [72.885, 21.175],
            [72.875, 21.198]
        ],
        "building_sqm": 60000,
        "road_sqm": 32000,
        "open_sqm": 12000,
        "water_sqm": 0,
        "tree_sqm": 4800,
        "base_temp": 46.9
    },
    {
        "area_id": 12,
        "zone_id": 4,
        "city_id": 1,
        "name": "Dindoli Lake & Planned Township",
        "code": "EZ-B03",
        "area_type": "Suburban Mixed Township",
        "description": "Dindoli lake catchment, new residential townships, wide road networks and open school grounds.",
        "polygon": [
            [72.845, 21.165],
            [72.885, 21.175],
            [72.920, 21.180],
            [72.905, 21.155],
            [72.870, 21.150],
            [72.845, 21.165]
        ],
        "building_sqm": 45000,
        "road_sqm": 26000,
        "open_sqm": 28000,
        "water_sqm": 12000,
        "tree_sqm": 11000,
        "base_temp": 44.2
    },

    # ── Zone 5: South Zone - Udhna (SZ-05) ──
    {
        "area_id": 13,
        "zone_id": 5,
        "city_id": 1,
        "name": "Pandesara GIDC Heavy Textile Dyeing Estate",
        "code": "SZ-A01",
        "area_type": "Heavy Industrial Estate",
        "description": "Massive chemical, textile dyeing & printing industrial sheds, metal roofing, extreme heat emissions.",
        "polygon": [
            [72.810, 21.135],
            [72.845, 21.135],
            [72.845, 21.160],
            [72.810, 21.160],
            [72.810, 21.135]
        ],
        "building_sqm": 82000,
        "road_sqm": 38000,
        "open_sqm": 4500,
        "water_sqm": 1000,
        "tree_sqm": 2200,
        "base_temp": 48.6
    },
    {
        "area_id": 14,
        "zone_id": 5,
        "city_id": 1,
        "name": "Udhna Railway Junction & Commercial Hub",
        "code": "SZ-A02",
        "area_type": "Transit & Commercial Hub",
        "description": "Railway yard, freight terminals, commercial market streets, asphalt parking plazas.",
        "polygon": [
            [72.810, 21.160],
            [72.845, 21.160],
            [72.845, 21.165],
            [72.838, 21.185],
            [72.820, 21.180],
            [72.810, 21.160]
        ],
        "building_sqm": 55000,
        "road_sqm": 42000,
        "open_sqm": 9000,
        "water_sqm": 0,
        "tree_sqm": 5500,
        "base_temp": 46.5
    },
    {
        "area_id": 15,
        "zone_id": 5,
        "city_id": 1,
        "name": "Bhestan & Unn Industrial Suburb",
        "code": "SZ-A03",
        "area_type": "Suburban Industrial & Housing",
        "description": "Textile labour housing quarters, industrial peripheral sheds, unpaved open soil verges.",
        "polygon": [
            [72.845, 21.135],
            [72.870, 21.150],
            [72.845, 21.165],
            [72.845, 21.135]
        ],
        "building_sqm": 48000,
        "road_sqm": 25000,
        "open_sqm": 32000,
        "water_sqm": 0,
        "tree_sqm": 7500,
        "base_temp": 45.3
    },

    # ── Zone 6: South-West Zone - Athwa (SWZ-06) ──
    {
        "area_id": 16,
        "zone_id": 6,
        "city_id": 1,
        "name": "Athwa Lines & Tapi Riverfront Promenade",
        "code": "SWZ-A01",
        "area_type": "Riverfront & Institutional",
        "description": "Government quarters, Tapi riverfront promenade, judicial courts, wide tree-lined boulevards.",
        "polygon": [
            [72.780, 21.165],
            [72.810, 21.160],
            [72.820, 21.180],
            [72.805, 21.185],
            [72.780, 21.165]
        ],
        "building_sqm": 35000,
        "road_sqm": 28000,
        "open_sqm": 22000,
        "water_sqm": 18000,
        "tree_sqm": 24000,
        "base_temp": 42.1
    },
    {
        "area_id": 17,
        "zone_id": 6,
        "city_id": 1,
        "name": "Vesu & SVNIT University Campus Area",
        "code": "SWZ-A02",
        "area_type": "Educational Campus & Planned Hub",
        "description": "Engineering university campuses, institutional botanical parks, modern planned high-rises.",
        "polygon": [
            [72.760, 21.135],
            [72.810, 21.135],
            [72.810, 21.160],
            [72.780, 21.165],
            [72.760, 21.135]
        ],
        "building_sqm": 40000,
        "road_sqm": 26000,
        "open_sqm": 38000,
        "water_sqm": 2500,
        "tree_sqm": 31000,
        "base_temp": 41.6
    },
    {
        "area_id": 18,
        "zone_id": 6,
        "city_id": 1,
        "name": "Piplod & Dumas Coastal Green Corridor",
        "code": "SWZ-A03",
        "area_type": "Coastal & Low-Density Tourism",
        "description": "Coastal mangrove verges, farmhouses, low-density recreational sectors, airport buffer.",
        "polygon": [
            [72.755, 21.145],
            [72.780, 21.165],
            [72.760, 21.135],
            [72.755, 21.145]
        ],
        "building_sqm": 22000,
        "road_sqm": 16000,
        "open_sqm": 55000,
        "water_sqm": 15000,
        "tree_sqm": 38000,
        "base_temp": 40.8
    },

    # ── Zone 7: West Zone - Rander (WZ-07) ──
    {
        "area_id": 19,
        "zone_id": 7,
        "city_id": 1,
        "name": "Rander Historic Heritage Town Sector",
        "code": "WZ-A01",
        "area_type": "Historic Town & Commercial",
        "description": "Ancient port town, dense historic residential quarters, mosques, historic riverbank steps.",
        "polygon": [
            [72.765, 21.175],
            [72.780, 21.165],
            [72.805, 21.185],
            [72.808, 21.202],
            [72.780, 21.202],
            [72.765, 21.175]
        ],
        "building_sqm": 48000,
        "road_sqm": 22000,
        "open_sqm": 12000,
        "water_sqm": 7000,
        "tree_sqm": 14000,
        "base_temp": 44.6
    },
    {
        "area_id": 20,
        "zone_id": 7,
        "city_id": 1,
        "name": "Adajan Commercial & Residential Center",
        "code": "WZ-A02",
        "area_type": "Prime Residential & Retail",
        "description": "High-density residential towers, shopping plazas, major arterial bridge connecting to Surat core.",
        "polygon": [
            [72.780, 21.202],
            [72.808, 21.202],
            [72.795, 21.245],
            [72.765, 21.235],
            [72.780, 21.202]
        ],
        "building_sqm": 56000,
        "road_sqm": 34000,
        "open_sqm": 16000,
        "water_sqm": 0,
        "tree_sqm": 12000,
        "base_temp": 43.8
    },
    {
        "area_id": 21,
        "zone_id": 7,
        "city_id": 1,
        "name": "Jahangirpura & Pal Botanical Suburb",
        "code": "WZ-A03",
        "area_type": "Suburban Green & Residential",
        "description": "Botanical gardens, Tapi river floodplains, low-rise residential societies, canal verges.",
        "polygon": [
            [72.750, 21.200],
            [72.765, 21.175],
            [72.765, 21.235],
            [72.750, 21.200]
        ],
        "building_sqm": 30000,
        "road_sqm": 20000,
        "open_sqm": 44000,
        "water_sqm": 11000,
        "tree_sqm": 26000,
        "base_temp": 42.2
    }
]

AHMEDABAD_AREAS = [
    # ── Zone 8: Central Zone (AMC-CZ-01) ──
    {
        "area_id": 22,
        "zone_id": 8,
        "city_id": 2,
        "name": "Kalupur & Old Walled Heritage Quarter",
        "code": "AMC-CZ-A01",
        "area_type": "Dense Commercial Heritage",
        "description": "Dense pol houses, historic wholesale bazaars, narrow street canyons with zero setbacks.",
        "polygon": [
            [72.585, 23.015],
            [72.605, 23.015],
            [72.605, 23.038],
            [72.585, 23.038],
            [72.585, 23.015]
        ],
        "building_sqm": 54000,
        "road_sqm": 24000,
        "open_sqm": 3000,
        "water_sqm": 0,
        "tree_sqm": 2500,
        "base_temp": 47.4
    },
    {
        "area_id": 23,
        "zone_id": 8,
        "city_id": 2,
        "name": "Bhadra Fort & Lal Darwaja Civic Market",
        "code": "AMC-CZ-A02",
        "area_type": "Civic & Retail Plaza",
        "description": "Historic citadel, major AMTS bus transit hub, high pedestrian footfalls, open paved plazas.",
        "polygon": [
            [72.565, 23.015],
            [72.585, 23.015],
            [72.585, 23.032],
            [72.565, 23.032],
            [72.565, 23.015]
        ],
        "building_sqm": 48000,
        "road_sqm": 32000,
        "open_sqm": 6000,
        "water_sqm": 0,
        "tree_sqm": 4200,
        "base_temp": 46.8
    },
    {
        "area_id": 24,
        "zone_id": 8,
        "city_id": 2,
        "name": "Shahpur & Sabarmati East Riverbank",
        "code": "AMC-CZ-A03",
        "area_type": "Mixed Residential & Riverbank",
        "description": "Historic riverside residences, metal sheet artisan workshops, municipal water works buffer.",
        "polygon": [
            [72.565, 23.032],
            [72.585, 23.032],
            [72.585, 23.045],
            [72.565, 23.045],
            [72.565, 23.032]
        ],
        "building_sqm": 42000,
        "road_sqm": 20000,
        "open_sqm": 12000,
        "water_sqm": 6000,
        "tree_sqm": 8000,
        "base_temp": 44.5
    },

    # ── Zone 9: North Zone (AMC-NZ-02) ──
    {
        "area_id": 25,
        "zone_id": 9,
        "city_id": 2,
        "name": "Naroda GIDC Industrial Estate",
        "code": "AMC-NZ-A01",
        "area_type": "Heavy Manufacturing Estate",
        "description": "Engineering and foundry fabrication sheds, heavy metal roofs, truck terminals.",
        "polygon": [
            [72.625, 23.060],
            [72.665, 23.060],
            [72.665, 23.085],
            [72.625, 23.095],
            [72.625, 23.060]
        ],
        "building_sqm": 76000,
        "road_sqm": 36000,
        "open_sqm": 8000,
        "water_sqm": 0,
        "tree_sqm": 3500,
        "base_temp": 48.0
    },
    {
        "area_id": 26,
        "zone_id": 9,
        "city_id": 2,
        "name": "Memco, Saijpur & Saraspur Rail Corridor",
        "code": "AMC-NZ-A02",
        "area_type": "Industrial & Worker Housing",
        "description": "Textile mill housing, railway logistics yard, densely packed middle-density housing.",
        "polygon": [
            [72.585, 23.045],
            [72.625, 23.045],
            [72.625, 23.070],
            [72.595, 23.070],
            [72.585, 23.045]
        ],
        "building_sqm": 58000,
        "road_sqm": 26000,
        "open_sqm": 10000,
        "water_sqm": 0,
        "tree_sqm": 6200,
        "base_temp": 46.2
    },
    {
        "area_id": 27,
        "zone_id": 9,
        "city_id": 2,
        "name": "Hansol & Airport Buffer Green Verge",
        "code": "AMC-NZ-A03",
        "area_type": "Institutional & Airport Buffer",
        "description": "Airport flight approach buffer, Sabarmati river bend, low-density cantonment green verge.",
        "polygon": [
            [72.595, 23.070],
            [72.645, 23.055],
            [72.665, 23.085],
            [72.625, 23.095],
            [72.595, 23.070]
        ],
        "building_sqm": 24000,
        "road_sqm": 18000,
        "open_sqm": 45000,
        "water_sqm": 8000,
        "tree_sqm": 28000,
        "base_temp": 41.9
    },

    # ── Zone 10: East Zone (AMC-EZ-03) ──
    {
        "area_id": 28,
        "zone_id": 10,
        "city_id": 2,
        "name": "Odhav Industrial Estate & Logistics Hub",
        "code": "AMC-EZ-A01",
        "area_type": "Industrial Logistics Estate",
        "description": "Massive chemical, engineering and logistics godowns with sheet roofing and unshaded paved yards.",
        "polygon": [
            [72.640, 23.000],
            [72.670, 23.000],
            [72.670, 23.030],
            [72.640, 23.030],
            [72.640, 23.000]
        ],
        "building_sqm": 80000,
        "road_sqm": 38000,
        "open_sqm": 6000,
        "water_sqm": 0,
        "tree_sqm": 2800,
        "base_temp": 48.2
    },
    {
        "area_id": 29,
        "zone_id": 10,
        "city_id": 2,
        "name": "Bapunagar & Gomtipur Worker Settlements",
        "code": "AMC-EZ-A02",
        "area_type": "Dense Residential Settlement",
        "description": "High-density diamond and textile artisan housing colonies, narrow streets, low vegetative cover.",
        "polygon": [
            [72.605, 23.015],
            [72.640, 23.015],
            [72.645, 23.055],
            [72.605, 23.038],
            [72.605, 23.015]
        ],
        "building_sqm": 68000,
        "road_sqm": 25000,
        "open_sqm": 5500,
        "water_sqm": 0,
        "tree_sqm": 3800,
        "base_temp": 47.1
    },
    {
        "area_id": 30,
        "zone_id": 10,
        "city_id": 2,
        "name": "Nikol & Amraiwadi Expansion Township",
        "code": "AMC-EZ-A03",
        "area_type": "Suburban Residential Township",
        "description": "Planned multistory residential apartments, wide arterial ring road connections, open amenity plots.",
        "polygon": [
            [72.615, 22.998],
            [72.665, 22.995],
            [72.670, 23.000],
            [72.615, 23.000],
            [72.615, 22.998]
        ],
        "building_sqm": 46000,
        "road_sqm": 26000,
        "open_sqm": 30000,
        "water_sqm": 2000,
        "tree_sqm": 9500,
        "base_temp": 44.7
    },

    # ── Zone 11: South Zone (AMC-SZ-04) ──
    {
        "area_id": 31,
        "zone_id": 11,
        "city_id": 2,
        "name": "Vatva GIDC Chemical & Industrial Complex",
        "code": "AMC-SZ-A01",
        "area_type": "Heavy Chemical & Dyeing Estate",
        "description": "Intense chemical dyeing, pharmaceutical factories, high waste heat emissions, asphalt freight lanes.",
        "polygon": [
            [72.600, 22.960],
            [72.665, 22.960],
            [72.665, 22.995],
            [72.615, 22.998],
            [72.600, 22.960]
        ],
        "building_sqm": 84000,
        "road_sqm": 42000,
        "open_sqm": 7000,
        "water_sqm": 0,
        "tree_sqm": 2500,
        "base_temp": 48.7
    },
    {
        "area_id": 32,
        "zone_id": 11,
        "city_id": 2,
        "name": "Maninagar & Kankaria Lakefront Hub",
        "code": "AMC-SZ-A02",
        "area_type": "Lakefront & Prime Residential",
        "description": "Kankaria Lake water body, urban recreational zoo buffer, high-density residential apartments.",
        "polygon": [
            [72.565, 22.985],
            [72.600, 22.985],
            [72.615, 22.998],
            [72.595, 23.015],
            [72.565, 23.015],
            [72.565, 22.985]
        ],
        "building_sqm": 44000,
        "road_sqm": 24000,
        "open_sqm": 22000,
        "water_sqm": 24000,
        "tree_sqm": 21000,
        "base_temp": 41.8
    },
    {
        "area_id": 33,
        "zone_id": 11,
        "city_id": 2,
        "name": "Danilimda & Behrampura Industrial Suburb",
        "code": "AMC-SZ-A03",
        "area_type": "Mixed Industrial & Slum Rehousing",
        "description": "Textile processing mills, unpaved open verges, densely built informal housing societies.",
        "polygon": [
            [72.565, 22.960],
            [72.600, 22.960],
            [72.600, 22.985],
            [72.565, 22.985],
            [72.565, 22.960]
        ],
        "building_sqm": 60000,
        "road_sqm": 28000,
        "open_sqm": 12000,
        "water_sqm": 0,
        "tree_sqm": 4500,
        "base_temp": 46.8
    },

    # ── Zone 12: West Zone (AMC-WZ-05) ──
    {
        "area_id": 34,
        "zone_id": 12,
        "city_id": 2,
        "name": "Navrangpura, CEPT & Gujarat University Campus",
        "code": "AMC-WZ-A01",
        "area_type": "Educational Campus & Institutional",
        "description": "University green campuses, institutional research parks, mature tree avenues, shaded sports grounds.",
        "polygon": [
            [72.535, 23.025],
            [72.565, 23.025],
            [72.565, 23.055],
            [72.535, 23.055],
            [72.535, 23.025]
        ],
        "building_sqm": 35000,
        "road_sqm": 22000,
        "open_sqm": 38000,
        "water_sqm": 0,
        "tree_sqm": 32000,
        "base_temp": 41.2
    },
    {
        "area_id": 35,
        "zone_id": 12,
        "city_id": 2,
        "name": "Ashram Road & Sabarmati West Promenade",
        "code": "AMC-WZ-A02",
        "area_type": "Commercial Arterial & Riverfront",
        "description": "Major corporate financial towers, Gandhi Ashram historic buffer, Sabarmati riverfront gardens.",
        "polygon": [
            [72.565, 23.010],
            [72.585, 23.045],
            [72.585, 23.070],
            [72.560, 23.080],
            [72.565, 23.010]
        ],
        "building_sqm": 46000,
        "road_sqm": 32000,
        "open_sqm": 18000,
        "water_sqm": 16000,
        "tree_sqm": 18000,
        "base_temp": 42.6
    },
    {
        "area_id": 36,
        "zone_id": 12,
        "city_id": 2,
        "name": "Paldi & Naranpura Prime Residential",
        "code": "AMC-WZ-A03",
        "area_type": "High-Value Residential",
        "description": "Organized housing societies, neighborhood municipal gardens, paved commercial avenues.",
        "polygon": [
            [72.535, 23.010],
            [72.565, 23.010],
            [72.565, 23.025],
            [72.530, 23.050],
            [72.535, 23.010]
        ],
        "building_sqm": 48000,
        "road_sqm": 24000,
        "open_sqm": 14000,
        "water_sqm": 0,
        "tree_sqm": 15000,
        "base_temp": 43.4
    },

    # ── Zone 13: New West Zone (AMC-NWZ-06) ──
    {
        "area_id": 37,
        "zone_id": 13,
        "city_id": 2,
        "name": "SG Highway Corporate & Commercial Corridor",
        "code": "AMC-NWZ-A01",
        "area_type": "High-Rise Commercial Hub",
        "description": "Glass-facade corporate towers, expansive asphalt parking lots, major multi-lane highway corridor.",
        "polygon": [
            [72.500, 23.020],
            [72.530, 23.020],
            [72.530, 23.050],
            [72.500, 23.050],
            [72.500, 23.020]
        ],
        "building_sqm": 62000,
        "road_sqm": 45000,
        "open_sqm": 16000,
        "water_sqm": 0,
        "tree_sqm": 6000,
        "base_temp": 45.8
    },
    {
        "area_id": 38,
        "zone_id": 13,
        "city_id": 2,
        "name": "Bodakdev & Thaltej Residential Sector",
        "code": "AMC-NWZ-A02",
        "area_type": "Upper-Income Residential & Clubs",
        "description": "Low-density bungalows, luxury high-rises, private club gardens, wide internal tree boulevards.",
        "polygon": [
            [72.500, 23.050],
            [72.530, 23.050],
            [72.530, 23.080],
            [72.500, 23.080],
            [72.500, 23.050]
        ],
        "building_sqm": 38000,
        "road_sqm": 22000,
        "open_sqm": 28000,
        "water_sqm": 3000,
        "tree_sqm": 22000,
        "base_temp": 42.0
    },
    {
        "area_id": 39,
        "zone_id": 13,
        "city_id": 2,
        "name": "Gota, Sola & Science City Expansion Ward",
        "code": "AMC-NWZ-A03",
        "area_type": "Rapid Expansion & Institutional",
        "description": "Science City educational park, ongoing construction zones, broad unshaded ring roads.",
        "polygon": [
            [72.470, 23.050],
            [72.500, 23.050],
            [72.500, 23.090],
            [72.470, 23.090],
            [72.470, 23.050]
        ],
        "building_sqm": 42000,
        "road_sqm": 30000,
        "open_sqm": 48000,
        "water_sqm": 4000,
        "tree_sqm": 12000,
        "base_temp": 43.9
    },

    # ── Zone 14: South West Zone (AMC-SWZ-07) ──
    {
        "area_id": 40,
        "zone_id": 14,
        "city_id": 2,
        "name": "Prahladnagar Corporate & Retail Boulevard",
        "code": "AMC-SWZ-A01",
        "area_type": "Prime Corporate Hub",
        "description": "High-density IT and banking offices, Prahladnagar Garden, paved retail boulevards.",
        "polygon": [
            [72.500, 22.990],
            [72.535, 22.990],
            [72.535, 23.020],
            [72.500, 23.020],
            [72.500, 22.990]
        ],
        "building_sqm": 58000,
        "road_sqm": 34000,
        "open_sqm": 14000,
        "water_sqm": 2000,
        "tree_sqm": 11000,
        "base_temp": 44.6
    },
    {
        "area_id": 41,
        "zone_id": 14,
        "city_id": 2,
        "name": "Sarkhej Roza Heritage & Lake Basin",
        "code": "AMC-SWZ-A02",
        "area_type": "Heritage Monument & Lake Basin",
        "description": "Historic Sarkhej Roza monument, seasonal lake basin, open peripheral soil grounds.",
        "polygon": [
            [72.480, 22.970],
            [72.520, 22.970],
            [72.520, 22.995],
            [72.480, 22.995],
            [72.480, 22.970]
        ],
        "building_sqm": 32000,
        "road_sqm": 18000,
        "open_sqm": 35000,
        "water_sqm": 14000,
        "tree_sqm": 16000,
        "base_temp": 42.8
    },
    {
        "area_id": 42,
        "zone_id": 14,
        "city_id": 2,
        "name": "Jodhpur, Vejalpur & Makarba Sector",
        "code": "AMC-SWZ-A03",
        "area_type": "Middle-Density Residential Hub",
        "description": "Residential societies, municipal school playgrounds, local community market lanes.",
        "polygon": [
            [72.520, 22.970],
            [72.565, 22.970],
            [72.565, 23.010],
            [72.520, 23.010],
            [72.520, 22.970]
        ],
        "building_sqm": 50000,
        "road_sqm": 26000,
        "open_sqm": 18000,
        "water_sqm": 0,
        "tree_sqm": 10500,
        "base_temp": 44.1
    }
]


def setup_planning_areas():
    db = SessionLocal()
    try:
        print("1. Creating 'planning_areas' table in PostgreSQL...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS planning_areas (
                area_id SERIAL PRIMARY KEY,
                zone_id INTEGER NOT NULL REFERENCES zones(zone_id),
                city_id INTEGER NOT NULL REFERENCES cities(city_id),
                name VARCHAR(150) NOT NULL,
                code VARCHAR(30) NOT NULL,
                area_type VARCHAR(50) NOT NULL,
                description TEXT,
                building_rooftop_sqm FLOAT NOT NULL DEFAULT 0,
                road_paved_sqm FLOAT NOT NULL DEFAULT 0,
                open_ground_sqm FLOAT NOT NULL DEFAULT 0,
                water_body_sqm FLOAT NOT NULL DEFAULT 0,
                existing_tree_cover_sqm FLOAT NOT NULL DEFAULT 0,
                avg_lst_summer FLOAT NOT NULL DEFAULT 42.0,
                peak_lst_summer FLOAT NOT NULL DEFAULT 46.0,
                geom geometry(MultiPolygon, 4326),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_planning_areas_geom ON planning_areas USING GIST (geom);
            CREATE INDEX IF NOT EXISTS idx_planning_areas_zone_id ON planning_areas (zone_id);
            CREATE INDEX IF NOT EXISTS idx_planning_areas_city_id ON planning_areas (city_id);
        """))
        db.commit()

        print("2. Populating 21 Surat & 21 Ahmedabad Planning Area Boundaries...")
        all_areas = SURAT_AREAS + AHMEDABAD_AREAS
        for a in all_areas:
            poly_coords = a["polygon"]
            wkt_coords = ", ".join([f"{coord[0]} {coord[1]}" for coord in poly_coords])
            wkt = f"MULTIPOLYGON((({wkt_coords})))"

            db.execute(text("""
                INSERT INTO planning_areas (
                    area_id, zone_id, city_id, name, code, area_type, description,
                    building_rooftop_sqm, road_paved_sqm, open_ground_sqm, water_body_sqm, existing_tree_cover_sqm,
                    avg_lst_summer, peak_lst_summer, geom
                )
                VALUES (
                    :aid, :zid, :cid, :name, :code, :atype, :desc,
                    :bsqm, :rsqm, :osqm, :wsqm, :tsqm,
                    :avg_t, :peak_t, ST_Multi(ST_GeomFromText(:wkt, 4326))
                )
                ON CONFLICT (area_id) DO UPDATE 
                SET name = EXCLUDED.name, 
                    code = EXCLUDED.code, 
                    area_type = EXCLUDED.area_type,
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

        # Add area_id column to grid_cells if not exists
        print("3. Adding area_id column to grid_cells and linking cells spatially...")
        db.execute(text("""
            ALTER TABLE grid_cells ADD COLUMN IF NOT EXISTS area_id INTEGER REFERENCES planning_areas(area_id);
            CREATE INDEX IF NOT EXISTS idx_grid_cells_area_id ON grid_cells(area_id);
        """))
        db.commit()

        # Spatially tag grid cells with their planning area
        db.execute(text("""
            UPDATE grid_cells gc
            SET area_id = pa.area_id
            FROM planning_areas pa
            WHERE gc.city_id = pa.city_id
              AND ST_Intersects(gc.centroid, pa.geom);
        """))
        db.commit()

        counts = db.execute(text("""
            SELECT pa.area_id, pa.code, pa.name, pa.city_id, count(gc.cell_id) as cell_count
            FROM planning_areas pa
            LEFT JOIN grid_cells gc ON gc.area_id = pa.area_id
            GROUP BY pa.area_id, pa.code, pa.name, pa.city_id
            ORDER BY pa.area_id;
        """)).fetchall()

        print("\nAll Planning Areas Configured Successfully:")
        for r in counts:
            print(f"  [City {r[3]}] [{r[1]}] {r[2]}: {r[4]:,} grid cells linked")

    finally:
        db.close()

if __name__ == "__main__":
    setup_planning_areas()

