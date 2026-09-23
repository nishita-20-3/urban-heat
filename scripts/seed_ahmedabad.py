import os
import json
import math
import random
from datetime import date
from sqlalchemy import text
from app.database import SessionLocal

# 7 Official Administrative Planning Zones of Ahmedabad Municipal Corporation (AMC)
# Exact geographic extents in WGS84 (SRID 4326)
AHMEDABAD_ZONES = [
    {
        "zone_id": 8,  # starting after Surat's 7 zones
        "name": "Central Zone",
        "code": "AMC-CZ-01",
        "description": "Old Walled City, Kalupur, Lal Darwaja, Astodia, Bhadra Fort, Shahpur. High thermal mass, narrow street canyons, intense microclimate heat retention.",
        "color": "#E8543E",
        "polygon": [
            [72.565, 23.015],
            [72.595, 23.015],
            [72.605, 23.038],
            [72.585, 23.045],
            [72.565, 23.032],
            [72.565, 23.015]
        ],
        "base_temp": 46.8,
        "built_up_ratio": 0.85,
        "tree_ratio": 0.05,
    },
    {
        "zone_id": 9,
        "name": "North Zone",
        "code": "AMC-NZ-02",
        "description": "Naroda, Memco, Saijpur, Saraspur, Sardarnagar, Hansol. Major industrial engineering clusters, textile mills, high waste heat emissions.",
        "color": "#F97316",
        "polygon": [
            [72.585, 23.045],
            [72.605, 23.038],
            [72.645, 23.055],
            [72.665, 23.085],
            [72.625, 23.095],
            [72.595, 23.070],
            [72.585, 23.045]
        ],
        "base_temp": 45.9,
        "built_up_ratio": 0.72,
        "tree_ratio": 0.10,
    },
    {
        "zone_id": 10,
        "name": "East Zone",
        "code": "AMC-EZ-03",
        "description": "Bapunagar, Gomtipur, Odhav Industrial Estate, Nikol, Amraiwadi. High-density worker housing settlements, tin/asbestos industrial roofs.",
        "color": "#D63031",
        "polygon": [
            [72.605, 23.038],
            [72.645, 23.055],
            [72.670, 23.030],
            [72.665, 22.995],
            [72.615, 22.998],
            [72.605, 23.038]
        ],
        "base_temp": 46.5,
        "built_up_ratio": 0.78,
        "tree_ratio": 0.06,
    },
    {
        "zone_id": 11,
        "name": "South Zone",
        "code": "AMC-SZ-04",
        "description": "Maninagar, Danilimda, Behrampura, Vatva GIDC Industrial Estate, Isanpur, Kankaria Lake. Chemical and textile industrial clusters, thermal hotspots.",
        "color": "#EF4444",
        "polygon": [
            [72.565, 22.960],
            [72.615, 22.960],
            [72.665, 22.995],
            [72.615, 22.998],
            [72.595, 23.015],
            [72.565, 23.015],
            [72.565, 22.960]
        ],
        "base_temp": 46.2,
        "built_up_ratio": 0.74,
        "tree_ratio": 0.08,
    },
    {
        "zone_id": 12,
        "name": "West Zone",
        "code": "AMC-WZ-05",
        "description": "Navrangpura, Usmanpura, Ambawadi, Naranpura, Paldi, Sabarmati Riverfront Promenade, Gujarat University. Major educational & institutional green corridors.",
        "color": "#14B8A6",
        "polygon": [
            [72.535, 23.010],
            [72.565, 23.010],
            [72.565, 23.045],
            [72.585, 23.070],
            [72.560, 23.080],
            [72.530, 23.050],
            [72.535, 23.010]
        ],
        "base_temp": 42.4,
        "built_up_ratio": 0.58,
        "tree_ratio": 0.22,
    },
    {
        "zone_id": 13,
        "name": "North-West Zone",
        "code": "AMC-NWZ-06",
        "description": "Bodakdev, Thaltej, Vastrapur Lake, Chandlodia, Gota, SG Highway IT Corridor. Modern commercial high-rises, planned retail plazas, mixed green verges.",
        "color": "#0FB5AE",
        "polygon": [
            [72.495, 23.035],
            [72.535, 23.035],
            [72.530, 23.050],
            [72.560, 23.080],
            [72.550, 23.110],
            [72.500, 23.090],
            [72.495, 23.035]
        ],
        "base_temp": 41.8,
        "built_up_ratio": 0.54,
        "tree_ratio": 0.24,
    },
    {
        "zone_id": 14,
        "name": "South-West Zone",
        "code": "AMC-SWZ-07",
        "description": "Satellite, Jodhpur, Prahlad Nagar, Vejalpur, Sarkhej Roza, Maktampura. Planned residential townships, institutional campuses, mixed suburban greenery.",
        "color": "#0284C7",
        "polygon": [
            [72.485, 22.975],
            [72.565, 22.975],
            [72.565, 23.010],
            [72.535, 23.010],
            [72.495, 23.035],
            [72.485, 22.975]
        ],
        "base_temp": 41.5,
        "built_up_ratio": 0.52,
        "tree_ratio": 0.25,
    }
]


def seed_ahmedabad():
    db = SessionLocal()
    try:
        print("1. Creating Ahmedabad in 'cities' table (city_id = 2)...")
        # Ensure city exists
        db.execute(text("""
            INSERT INTO cities (city_id, name, state, boundary, is_prototype)
            VALUES (
                2, 
                'Ahmedabad', 
                'Gujarat', 
                ST_Multi(ST_MakeEnvelope(72.48, 22.96, 72.67, 23.11, 4326)),
                TRUE
            )
            ON CONFLICT (city_id) DO UPDATE 
            SET name = EXCLUDED.name, state = EXCLUDED.state, boundary = EXCLUDED.boundary;
        """))
        db.commit()

        print("2. Populating Ahmedabad Municipal Corporation (AMC) 7 Zones...")
        for z in AHMEDABAD_ZONES:
            poly_coords = z["polygon"]
            wkt_coords = ", ".join([f"{coord[0]} {coord[1]}" for coord in poly_coords])
            wkt = f"MULTIPOLYGON((({wkt_coords})))"

            db.execute(text("""
                INSERT INTO zones (zone_id, city_id, name, code, description, color, geom)
                VALUES (:zid, 2, :name, :code, :desc, :color, ST_Multi(ST_GeomFromText(:wkt, 4326)))
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

        # Step 3: Generate ~2,500 grid cells for Ahmedabad across all 7 zones
        print("3. Generating high-resolution microclimate grid cells for Ahmedabad...")
        
        # Clean existing Ahmedabad cells to avoid duplicates if re-run
        db.execute(text("""
            DELETE FROM recommendations WHERE cell_id IN (SELECT cell_id FROM grid_cells WHERE city_id = 2);
            DELETE FROM feasibility_caps WHERE cell_id IN (SELECT cell_id FROM grid_cells WHERE city_id = 2);
            DELETE FROM heat_predictions WHERE cell_id IN (SELECT cell_id FROM grid_cells WHERE city_id = 2);
            DELETE FROM lulc_classification WHERE cell_id IN (SELECT cell_id FROM grid_cells WHERE city_id = 2);
            DELETE FROM satellite_observations WHERE cell_id IN (SELECT cell_id FROM grid_cells WHERE city_id = 2);
            DELETE FROM grid_cells WHERE city_id = 2;
        """))
        db.commit()

        # Get max cell_id to start from
        max_id = db.execute(text("SELECT COALESCE(MAX(cell_id), 800000) FROM grid_cells")).scalar()
        current_cell_id = max_id + 1

        # Grid generation parameters (~200m resolution for fast performance)
        step = 0.0022

        grid_cells_data = []
        lulc_data = []
        predictions_data = []
        feasibility_data = []
        recommendations_data = []

        random.seed(42)

        # Generate cells for each zone polygon
        for z in AHMEDABAD_ZONES:
            zid = z["zone_id"]
            poly = z["polygon"]
            min_lng = min(p[0] for p in poly)
            max_lng = max(p[0] for p in poly)
            min_lat = min(p[1] for p in poly)
            max_lat = max(p[1] for p in poly)

            lng = min_lng + step / 2
            while lng < max_lng:
                lat = min_lat + step / 2
                while lat < max_lat:
                    poly_wkt = f"POLYGON(({lng} {lat}, {lng + step*0.92} {lat}, {lng + step*0.92} {lat + step*0.92}, {lng} {lat + step*0.92}, {lng} {lat}))"
                    centroid_wkt = f"POINT({lng + step*0.46} {lat + step*0.46})"
                    
                    cid = current_cell_id
                    current_cell_id += 1

                    grid_cells_data.append({
                        "cid": cid,
                        "zid": zid,
                        "geom": poly_wkt,
                        "centroid": centroid_wkt
                    })

                    # Calculate realistic LULC based on zone profile
                    built_ratio = z["built_up_ratio"] + random.uniform(-0.08, 0.06)
                    built_ratio = max(0.25, min(0.90, built_ratio))
                    tree_ratio = z["tree_ratio"] + random.uniform(-0.03, 0.05)
                    tree_ratio = max(0.02, min(0.35, tree_ratio))
                    water_ratio = 0.05 if (72.56 <= lng <= 72.58 and 23.00 <= lat <= 23.06) else 0.0
                    open_ratio = max(0.05, 1.0 - built_ratio - tree_ratio - water_ratio)

                    built_sqm = round(built_ratio * 10000.0, 1)
                    tree_sqm = round(tree_ratio * 10000.0, 1)
                    open_sqm = round(open_ratio * 10000.0, 1)
                    water_sqm = round(water_ratio * 10000.0, 1)

                    # LULC rows
                    lulc_data.append({"cid": cid, "class_id": 50, "cname": "Built-up", "sqm": built_sqm})
                    lulc_data.append({"cid": cid, "class_id": 10, "cname": "Tree cover", "sqm": tree_sqm})
                    lulc_data.append({"cid": cid, "class_id": 30, "cname": "Grassland", "sqm": open_sqm})
                    if water_sqm > 0:
                        lulc_data.append({"cid": cid, "class_id": 80, "cname": "Permanent water bodies", "sqm": water_sqm})

                    # Calculate seasonal temperatures based on LULC and Zone
                    ndbi = (built_ratio - tree_ratio) * 0.6 + 0.1
                    ndvi = tree_ratio * 1.5 + open_ratio * 0.3
                    
                    summer_lst = round(z["base_temp"] + (built_ratio * 2.8) - (tree_ratio * 4.0) - (water_ratio * 5.0) + random.uniform(-0.6, 0.6), 1)
                    monsoon_lst = round(summer_lst - 11.5 + random.uniform(-0.4, 0.4), 1)
                    winter_lst = round(summer_lst - 18.0 + random.uniform(-0.5, 0.5), 1)

                    # Predictions
                    shap_obj = {
                        "base_value": 38.5,
                        "contributions": {
                            "ndbi": round(ndbi * 3.2, 3),
                            "ndvi": round(-ndvi * 2.8, 3),
                            "air_temp": round(random.uniform(4.5, 5.5), 3),
                            "wind_speed": round(-random.uniform(0.8, 1.4), 3),
                            "Built-up_pct": round(built_ratio * 2.5, 3),
                            "Tree cover_pct": round(-tree_ratio * 3.0, 3),
                        }
                    }

                    predictions_data.append({
                        "cid": cid, "season": "summer", "pred_lst": summer_lst, "actual_lst": round(summer_lst + random.uniform(-0.3, 0.3), 1),
                        "cooling_gap": round(max(0.5, summer_lst - 38.0), 1), "shap": json.dumps(shap_obj)
                    })
                    predictions_data.append({
                        "cid": cid, "season": "monsoon", "pred_lst": monsoon_lst, "actual_lst": None,
                        "cooling_gap": 0.8, "shap": json.dumps({"base_value": 31.0, "contributions": {"ndvi": -0.5, "ndbi": 0.8}})
                    })
                    predictions_data.append({
                        "cid": cid, "season": "winter", "pred_lst": winter_lst, "actual_lst": None,
                        "cooling_gap": 0.2, "shap": json.dumps({"base_value": 25.0, "contributions": {"ndvi": -0.2, "ndbi": 0.4}})
                    })

                    # Feasibility Caps
                    cool_roof_cap = round(built_sqm * 0.40, 0)
                    tree_cap = round(open_sqm / 35.0, 0)
                    park_cap = round(open_sqm * 0.20, 0)
                    pavement_cap = round(built_sqm * 0.10, 0)
                    green_wall_cap = round(built_sqm * 0.08, 0)

                    feasibility_data.extend([
                        {"cid": cid, "iid": 1, "cap": tree_cap},
                        {"cid": cid, "iid": 2, "cap": cool_roof_cap},
                        {"cid": cid, "iid": 3, "cap": park_cap},
                        {"cid": cid, "iid": 4, "cap": pavement_cap},
                        {"cid": cid, "iid": 5, "cap": green_wall_cap},
                    ])

                    # Realistic recommendations (Balanced, Max Cooling, Budget)
                    recs_balanced = [
                        {"cid": cid, "scen": "balanced", "iid": 2, "qty": round(cool_roof_cap * 0.5, 0), "cool": round(cool_roof_cap * 0.5 * 0.003, 2), "cost": round(cool_roof_cap * 0.5 * 150.0, 2)},
                        {"cid": cid, "scen": "balanced", "iid": 1, "qty": round(tree_cap * 0.5, 0), "cool": round(tree_cap * 0.5 * 0.05, 2), "cost": round(tree_cap * 0.5 * 300.0, 2)},
                        {"cid": cid, "scen": "balanced", "iid": 3, "qty": round(park_cap * 0.5, 0), "cool": round(park_cap * 0.5 * 0.002, 2), "cost": round(park_cap * 0.5 * 250.0, 2)},
                    ]
                    recs_max = [
                        {"cid": cid, "scen": "max_cooling", "iid": 2, "qty": round(cool_roof_cap * 0.8, 0), "cool": round(cool_roof_cap * 0.8 * 0.003, 2), "cost": round(cool_roof_cap * 0.8 * 150.0, 2)},
                        {"cid": cid, "scen": "max_cooling", "iid": 1, "qty": round(tree_cap * 0.8, 0), "cool": round(tree_cap * 0.8 * 0.05, 2), "cost": round(tree_cap * 0.8 * 300.0, 2)},
                        {"cid": cid, "scen": "max_cooling", "iid": 3, "qty": round(park_cap * 0.8, 0), "cool": round(park_cap * 0.8 * 0.002, 2), "cost": round(park_cap * 0.8 * 250.0, 2)},
                        {"cid": cid, "scen": "max_cooling", "iid": 4, "qty": round(pavement_cap * 0.8, 0), "cool": round(pavement_cap * 0.8 * 0.001, 2), "cost": round(pavement_cap * 0.8 * 1200.0, 2)},
                    ]
                    recs_budget = [
                        {"cid": cid, "scen": "budget", "iid": 2, "qty": round(cool_roof_cap * 0.3, 0), "cool": round(cool_roof_cap * 0.3 * 0.003, 2), "cost": round(cool_roof_cap * 0.3 * 150.0, 2)},
                        {"cid": cid, "scen": "budget", "iid": 1, "qty": round(tree_cap * 0.3, 0), "cool": round(tree_cap * 0.3 * 0.05, 2), "cost": round(tree_cap * 0.3 * 300.0, 2)},
                    ]

                    recommendations_data.extend(recs_balanced)
                    recommendations_data.extend(recs_max)
                    recommendations_data.extend(recs_budget)

                    lat += step
                lng += step

        print(f"4. Inserting {len(grid_cells_data):,} grid cells for Ahmedabad...")
        batch_size = 500
        for i in range(0, len(grid_cells_data), batch_size):
            chunk = grid_cells_data[i:i+batch_size]
            for row in chunk:
                db.execute(text("""
                    INSERT INTO grid_cells (cell_id, city_id, zone_id, geom, centroid)
                    VALUES (:cid, 2, :zid, ST_GeomFromText(:geom, 4326), ST_GeomFromText(:centroid, 4326))
                """), row)
            db.commit()

        print(f"5. Inserting {len(lulc_data):,} LULC classification records...")
        for i in range(0, len(lulc_data), batch_size):
            chunk = lulc_data[i:i+batch_size]
            for row in chunk:
                db.execute(text("""
                    INSERT INTO lulc_classification (cell_id, lulc_class, class_name, pixel_count, area_sqm, year)
                    VALUES (:cid, :class_id, :cname, :sqm / 100.0, :sqm, 2026)
                """), row)
            db.commit()

        print(f"6. Inserting {len(predictions_data):,} Heat Predictions with SHAP values...")
        for i in range(0, len(predictions_data), batch_size):
            chunk = predictions_data[i:i+batch_size]
            for row in chunk:
                db.execute(text("""
                    INSERT INTO heat_predictions (cell_id, season, prediction_date, predicted_lst, actual_lst, cooling_gap, shap_values, model_version)
                    VALUES (:cid, :season, '2026-08-18', :pred_lst, :actual_lst, :cooling_gap, CAST(:shap AS jsonb), 'v1.0.0-amc')
                """), row)
            db.commit()

        print(f"7. Inserting {len(feasibility_data):,} Feasibility Caps...")
        for i in range(0, len(feasibility_data), batch_size):
            chunk = feasibility_data[i:i+batch_size]
            for row in chunk:
                db.execute(text("""
                    INSERT INTO feasibility_caps (cell_id, intervention_id, feasibility_cap_sqm)
                    VALUES (:cid, :iid, :cap)
                """), row)
            db.commit()

        print(f"8. Inserting {len(recommendations_data):,} Costed Recommendations...")
        for i in range(0, len(recommendations_data), batch_size):
            chunk = recommendations_data[i:i+batch_size]
            for row in chunk:
                db.execute(text("""
                    INSERT INTO recommendations (cell_id, scenario_type, intervention_id, recommended_quantity, expected_cooling_contribution, estimated_cost)
                    VALUES (:cid, :scen, :iid, :qty, :cool, :cost)
                """), row)
            db.commit()

        print("\nAhmedabad Data Seeded Successfully!")
        print(f"  City: Ahmedabad, Gujarat (city_id = 2)")
        print(f"  Zones: 7 AMC Administrative Planning Zones")
        print(f"  Grid Cells: {len(grid_cells_data):,} high-resolution microclimate cells")
        print(f"  Predictions: {len(predictions_data):,} seasonal records with SHAP")
        print(f"  Recommendations: {len(recommendations_data):,} costed feasibility packages")

    finally:
        db.close()

if __name__ == "__main__":
    seed_ahmedabad()
