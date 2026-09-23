import json
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.spatial import Zone, City
from app.schemas.zone import (
    ZoneFeatureCollection,
    ZoneFeature,
    ZoneProperties,
    ZoneSummaryResponse,
    TopInterventionSummary,
)


def get_zones_for_city(
    db: Session,
    city_id: int,
    season: str = "summer",
) -> ZoneFeatureCollection:
    """
    Returns GeoJSON FeatureCollection of all administrative zones for a city with aggregated
    temperature, hotspot count, LULC area, budget, and priority levels in a single optimized query.
    """
    city_exists = db.query(City.city_id).filter(City.city_id == city_id).scalar()
    if not city_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City with id {city_id} not found",
        )

    # Aggregated query per zone
    query = text("""
        WITH zone_preds AS (
            SELECT 
                gc.zone_id,
                COUNT(DISTINCT gc.cell_id) as total_cells,
                COUNT(DISTINCT CASE WHEN hp.predicted_lst >= 40.0 THEN gc.cell_id END) as hotspot_cells,
                COALESCE(AVG(hp.predicted_lst), 38.5) as avg_lst,
                COALESCE(MAX(hp.predicted_lst), 45.0) as peak_lst
            FROM grid_cells gc
            LEFT JOIN heat_predictions hp 
                ON hp.cell_id = gc.cell_id 
               AND LOWER(hp.season) = LOWER(:season)
            WHERE gc.city_id = :city_id AND gc.zone_id IS NOT NULL
            GROUP BY gc.zone_id
        ),
        zone_lulc AS (
            SELECT 
                gc.zone_id,
                COALESCE(SUM(CASE WHEN l.class_name = 'Built-up' THEN l.area_sqm ELSE 0 END), 0) as built_up_sqm,
                COALESCE(SUM(CASE WHEN l.class_name IN ('Grassland', 'Cropland', 'Bare / sparse vegetation') THEN l.area_sqm ELSE 0 END), 0) as open_soil_sqm,
                COALESCE(SUM(CASE WHEN l.class_name = 'Tree cover' THEN l.area_sqm ELSE 0 END), 0) as tree_sqm
            FROM grid_cells gc
            JOIN lulc_classification l ON l.cell_id = gc.cell_id
            WHERE gc.city_id = :city_id AND gc.zone_id IS NOT NULL
            GROUP BY gc.zone_id
        ),
        zone_recs AS (
            SELECT 
                gc.zone_id,
                -- Realistic Priority Pilot Cluster Budget (top 5-10 hotspot cells package)
                COALESCE(AVG(r.estimated_cost), 350000.0) * 8.0 as total_budget,
                COALESCE(AVG(r.expected_cooling_contribution), 1.8) as avg_cooling
            FROM grid_cells gc
            JOIN recommendations r ON r.cell_id = gc.cell_id AND r.scenario_type = 'balanced'
            WHERE gc.city_id = :city_id AND gc.zone_id IS NOT NULL
            GROUP BY gc.zone_id
        )
        SELECT 
            z.zone_id,
            z.name,
            z.code,
            z.description,
            z.color,
            ST_AsGeoJSON(z.geom) as geojson_geom,
            COALESCE(zp.avg_lst, 38.0) as avg_lst,
            COALESCE(zp.peak_lst, 42.0) as peak_lst,
            COALESCE(zp.hotspot_cells, 0) as hotspot_cells,
            COALESCE(zp.total_cells, 0) as total_cells,
            COALESCE(zl.built_up_sqm, 0) as built_up_sqm,
            COALESCE(zl.open_soil_sqm, 0) as open_soil_sqm,
            COALESCE(zl.tree_sqm, 0) as tree_sqm,
            COALESCE(zr.total_budget, 2800000.0) as total_budget,
            COALESCE(zr.avg_cooling, 1.8) as avg_cooling
        FROM zones z
        LEFT JOIN zone_preds zp ON zp.zone_id = z.zone_id
        LEFT JOIN zone_lulc zl ON zl.zone_id = z.zone_id
        LEFT JOIN zone_recs zr ON zr.zone_id = z.zone_id
        WHERE z.city_id = :city_id
        ORDER BY z.zone_id;
    """)

    results = db.execute(query, {"city_id": city_id, "season": season}).fetchall()

    features: List[ZoneFeature] = []
    for row in results:
        zone_id = row[0]
        name = row[1]
        code = row[2]
        description = row[3]
        color = row[4]
        raw_geom = row[5]
        avg_lst = float(row[6])
        peak_lst = float(row[7])
        hotspot_cells = int(row[8])
        total_cells = int(row[9])
        built_up_sqm = float(row[10])
        open_soil_sqm = float(row[11])
        tree_sqm = float(row[12])
        total_budget = float(row[13])
        avg_cooling = float(row[14])

        # Compute priority level
        if avg_lst >= 42.0 or hotspot_cells >= 200:
            priority = "High"
        elif avg_lst >= 38.0 or hotspot_cells >= 50:
            priority = "Moderate"
        else:
            priority = "Low"

        geom_dict = json.loads(raw_geom) if isinstance(raw_geom, str) else raw_geom

        features.append(
            ZoneFeature(
                geometry=geom_dict,
                properties=ZoneProperties(
                    zone_id=zone_id,
                    name=name,
                    code=code,
                    description=description,
                    color=color,
                    avg_lst=round(avg_lst, 1),
                    peak_lst=round(peak_lst, 1),
                    hotspot_cell_count=hotspot_cells,
                    total_cell_count=total_cells,
                    priority_level=priority,
                    built_up_area_sqm=round(built_up_sqm, 0),
                    open_area_sqm=round(open_soil_sqm, 0),
                    green_cover_sqm=round(tree_sqm, 0),
                    total_budget_inr=round(total_budget, 2),
                    avg_cooling_potential_c=round(avg_cooling, 2),
                ),
            )
        )

    return ZoneFeatureCollection(features=features)


def get_zone_summary(
    db: Session,
    zone_id: int,
    season: str = "summer",
) -> ZoneSummaryResponse:
    """
    Returns deep-dive summary metrics and top 4 interventions for a specific zone.
    """
    zone_row = (
        db.query(Zone.zone_id, Zone.name, Zone.code, Zone.description, Zone.color)
        .filter(Zone.zone_id == zone_id)
        .first()
    )
    if not zone_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone with id {zone_id} not found",
        )

    # Get aggregate stats
    stats_query = text("""
        SELECT 
            COALESCE(AVG(hp.predicted_lst), 38.0) as avg_lst,
            COALESCE(MAX(hp.predicted_lst), 42.0) as peak_lst,
            COUNT(DISTINCT CASE WHEN hp.predicted_lst >= 40.0 THEN gc.cell_id END) as hotspot_cells,
            COUNT(DISTINCT gc.cell_id) as total_cells,
            COALESCE(SUM(CASE WHEN l.class_name = 'Built-up' THEN l.area_sqm ELSE 0 END), 0) as built_up_sqm,
            COALESCE(SUM(CASE WHEN l.class_name IN ('Grassland', 'Cropland', 'Bare / sparse vegetation') THEN l.area_sqm ELSE 0 END), 0) as open_soil_sqm,
            COALESCE(SUM(CASE WHEN l.class_name = 'Tree cover' THEN l.area_sqm ELSE 0 END), 0) as tree_sqm,
            COALESCE(SUM(CASE WHEN l.class_name = 'Permanent water bodies' THEN l.area_sqm ELSE 0 END), 0) as water_sqm,
            COALESCE(AVG(r.estimated_cost), 350000.0) * 8.0 as total_budget,
            COALESCE(AVG(r.expected_cooling_contribution), 1.8) as avg_cooling
        FROM grid_cells gc
        LEFT JOIN heat_predictions hp ON hp.cell_id = gc.cell_id AND LOWER(hp.season) = LOWER(:season)
        LEFT JOIN lulc_classification l ON l.cell_id = gc.cell_id
        LEFT JOIN recommendations r ON r.cell_id = gc.cell_id AND r.scenario_type = 'balanced'
        WHERE gc.zone_id = :zone_id;
    """)
    stats = db.execute(stats_query, {"zone_id": zone_id, "season": season}).fetchone()

    # Get top 4 interventions scaled to a realistic priority pilot cluster (8 cells)
    top_int_query = text("""
        SELECT 
            it.name,
            COALESCE(AVG(r.recommended_quantity), 0) * 8.0 as total_qty,
            it.unit,
            COALESCE(AVG(r.expected_cooling_contribution), 0) as avg_cooling,
            COALESCE(AVG(r.estimated_cost), 0) * 8.0 as total_cost
        FROM grid_cells gc
        JOIN recommendations r ON r.cell_id = gc.cell_id AND r.scenario_type = 'balanced'
        JOIN intervention_types it ON it.intervention_id = r.intervention_id
        WHERE gc.zone_id = :zone_id
        GROUP BY it.name, it.unit
        ORDER BY total_cost DESC
        LIMIT 4;
    """)
    top_ints = db.execute(top_int_query, {"zone_id": zone_id}).fetchall()

    top_interventions = [
        TopInterventionSummary(
            name=row[0],
            display_name=row[0].replace("_", " ").title(),
            total_quantity=round(float(row[1]), 1),
            unit=row[2],
            total_cooling_c=round(float(row[3]), 2),
            total_cost_inr=round(float(row[4]), 2),
        )
        for row in top_ints
    ]

    avg_lst = float(stats[0]) if stats and stats[0] is not None else 38.0
    hotspot_cells = int(stats[2]) if stats and stats[2] is not None else 0
    priority = "High" if (avg_lst >= 42.0 or hotspot_cells >= 200) else "Moderate" if (avg_lst >= 38.0 or hotspot_cells >= 50) else "Low"

    return ZoneSummaryResponse(
        zone_id=zone_row[0],
        name=zone_row[1],
        code=zone_row[2],
        description=zone_row[3],
        color=zone_row[4],
        priority_level=priority,
        avg_lst=round(avg_lst, 1),
        peak_lst=round(float(stats[1]) if stats and stats[1] is not None else 42.0, 1),
        hotspot_cell_count=hotspot_cells,
        total_cell_count=int(stats[3]) if stats and stats[3] is not None else 0,
        built_up_sqm=round(float(stats[4]) if stats and stats[4] is not None else 0.0, 0),
        open_soil_sqm=round(float(stats[5]) if stats and stats[5] is not None else 0.0, 0),
        tree_cover_sqm=round(float(stats[6]) if stats and stats[6] is not None else 0.0, 0),
        water_sqm=round(float(stats[7]) if stats and stats[7] is not None else 0.0, 0),
        total_budget_inr=round(float(stats[8]) if stats and stats[8] is not None else 2800000.0, 2),
        avg_cooling_potential_c=round(float(stats[9]) if stats and stats[9] is not None else 1.8, 2),
        top_interventions=top_interventions,
    )
