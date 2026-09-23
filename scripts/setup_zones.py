import os
import json
from sqlalchemy import text
from app.database import engine, SessionLocal

# Official 7 Administrative Planning Zones of Surat Municipal Corporation (SMC)
# Smooth, contiguous boundaries following Surat's urban extent and Tapi river course
SURAT_ZONES = [
    {
        "zone_id": 1,
        "name": "Central Zone",
        "code": "CZ-01",
        "description": "Old Walled City, Muglisara, Chowk Bazaar, Nanpura, Shahpore. Dense historic built-up commercial core with narrow street canyons and high thermal retention.",
        "color": "#E8543E",
        "polygon": [
            [72.805, 21.185],
            [72.820, 21.180],
            [72.838, 21.185],
            [72.842, 21.198],
            [72.836, 21.208],
            [72.820, 21.212],
            [72.808, 21.202],
            [72.805, 21.185]
        ]
    },
    {
        "zone_id": 2,
        "name": "North Zone (Katargam)",
        "code": "NZ-02",
        "description": "Katargam, Amroli, Singanpore, Gotalawadi, Kosad. Major diamond cutting hub, high density residential clusters and industrial rooftops.",
        "color": "#F97316",
        "polygon": [
            [72.808, 21.202],
            [72.820, 21.212],
            [72.836, 21.208],
            [72.855, 21.225],
            [72.868, 21.250],
            [72.850, 21.270],
            [72.820, 21.265],
            [72.795, 21.245],
            [72.808, 21.202]
        ]
    },
    {
        "zone_id": 3,
        "name": "East Zone-A (Varachha)",
        "code": "EZ-03",
        "description": "Varachha, Kapodra, Nana Varachha, Karanj, Sarthana. High-density textile & diamond trading markets, heavy concrete and paved surfaces.",
        "color": "#EF4444",
        "polygon": [
            [72.836, 21.208],
            [72.842, 21.198],
            [72.875, 21.198],
            [72.905, 21.215],
            [72.915, 21.245],
            [72.885, 21.255],
            [72.855, 21.225],
            [72.836, 21.208]
        ]
    },
    {
        "zone_id": 4,
        "name": "East Zone-B (Limbayat)",
        "code": "EZ-04",
        "description": "Limbayat, Dindoli, Godadara, Parvat Patiya. Dense migrant worker housing colonies, tin-roof settlements, high vulnerable heat exposure.",
        "color": "#D63031",
        "polygon": [
            [72.838, 21.185],
            [72.842, 21.198],
            [72.875, 21.198],
            [72.905, 21.215],
            [72.920, 21.180],
            [72.905, 21.155],
            [72.870, 21.150],
            [72.845, 21.165],
            [72.838, 21.185]
        ]
    },
    {
        "zone_id": 5,
        "name": "South Zone (Udhna)",
        "code": "SZ-05",
        "description": "Udhna, Pandesara Industrial Estate, Bhestan, Unn. Heavy textile dyeing/printing mills, industrial metal shed roofs, intense waste heat emissions.",
        "color": "#F59E0B",
        "polygon": [
            [72.810, 21.135],
            [72.845, 21.135],
            [72.870, 21.150],
            [72.845, 21.165],
            [72.838, 21.185],
            [72.820, 21.180],
            [72.810, 21.160],
            [72.810, 21.135]
        ]
    },
    {
        "zone_id": 6,
        "name": "South-West Zone (Athwa)",
        "code": "SWZ-06",
        "description": "Athwa, Piplod, Vesu, City Light, Dumas, Magdalla. Modern planned residential developments, institutional campuses, coastal open spaces, riverfront promenades.",
        "color": "#0FB5AE",
        "polygon": [
            [72.760, 21.135],
            [72.810, 21.135],
            [72.810, 21.160],
            [72.820, 21.180],
            [72.805, 21.185],
            [72.780, 21.165],
            [72.755, 21.145],
            [72.760, 21.135]
        ]
    },
    {
        "zone_id": 7,
        "name": "West Zone (Rander)",
        "code": "WZ-07",
        "description": "Rander, Adajan, Jahangirpura, Pal. Trans-Tapi residential suburbs, historic botanical gardens, mixed residential townships with moderate canopy cover.",
        "color": "#14B8A6",
        "polygon": [
            [72.765, 21.175],
            [72.780, 21.165],
            [72.805, 21.185],
            [72.808, 21.202],
            [72.795, 21.245],
            [72.765, 21.235],
            [72.750, 21.200],
            [72.765, 21.175]
        ]
    }
]


def setup_zones():
    db = SessionLocal()
    try:
        print("1. Updating Surat Municipal Corporation Zones with smooth natural boundaries...")
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

        print("2. Spatially assigning grid cells to their respective SMC zones...")
        db.execute(text("""
            UPDATE grid_cells gc
            SET zone_id = z.zone_id
            FROM zones z
            WHERE gc.city_id = z.city_id
              AND ST_Intersects(gc.centroid, z.geom);
        """))
        db.commit()

        counts = db.execute(text("""
            SELECT z.zone_id, z.name, count(gc.cell_id) as cell_count
            FROM zones z
            LEFT JOIN grid_cells gc ON gc.zone_id = z.zone_id
            GROUP BY z.zone_id, z.name
            ORDER BY z.zone_id;
        """)).fetchall()

        print("\nSMC Zones Updated Successfully:")
        for r in counts:
            print(f"  [{r[0]}] {r[1]}: {r[2]:,} grid cells mapped")

    finally:
        db.close()

if __name__ == "__main__":
    setup_zones()
