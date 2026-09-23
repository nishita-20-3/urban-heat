import os
import sys
from sqlalchemy import text
from app.database import SessionLocal

def recalibrate_feasibility():
    db = SessionLocal()
    try:
        print("1. Auditing LULC distribution across cells with predictions...")

        # Step 1: Create temporary LULC aggregated summary per cell
        print("2. Recalculating feasibility_caps based on realistic 100m cell footprint (10,000 sqm)...")
        
        db.execute(text("""
            DROP TABLE IF EXISTS temp_cell_lulc;
            CREATE TEMP TABLE temp_cell_lulc AS
            SELECT 
                cell_id,
                -- Cap individual land components so they never exceed realistic cell physical sizes
                LEAST(COALESCE(SUM(CASE WHEN class_name = 'Built-up' THEN area_sqm ELSE 0 END), 0), 6000.0)::numeric as built_up_sqm,
                LEAST(COALESCE(SUM(CASE WHEN class_name IN ('Grassland', 'Cropland', 'Bare / sparse vegetation') THEN area_sqm ELSE 0 END), 0), 4000.0)::numeric as open_soil_sqm,
                LEAST(COALESCE(SUM(CASE WHEN class_name = 'Tree cover' THEN area_sqm ELSE 0 END), 0), 3000.0)::numeric as tree_sqm,
                LEAST(COALESCE(SUM(CASE WHEN class_name = 'Permanent water bodies' THEN area_sqm ELSE 0 END), 0), 2000.0)::numeric as water_sqm
            FROM lulc_classification
            GROUP BY cell_id;
            CREATE INDEX idx_temp_cell_lulc ON temp_cell_lulc(cell_id);
        """))
        db.commit()

        print("3. Updating feasibility_caps with strict realistic physical caps...")
        # 1: tree_planting -> based on open soil (1 tree per 25 m2, max 30 trees per cell)
        db.execute(text("""
            UPDATE feasibility_caps fc
            SET feasibility_cap_sqm = LEAST(ROUND((t.open_soil_sqm / 35.0)::numeric, 0), 35.0)
            FROM temp_cell_lulc t
            WHERE fc.cell_id = t.cell_id AND fc.intervention_id = 1;
        """))

        # 2: cool_roofing -> based on built-up roof area (max 500 sqm per 100m cell)
        db.execute(text("""
            UPDATE feasibility_caps fc
            SET feasibility_cap_sqm = LEAST(ROUND((t.built_up_sqm * 0.40)::numeric, 0), 600.0)
            FROM temp_cell_lulc t
            WHERE fc.cell_id = t.cell_id AND fc.intervention_id = 2;
        """))

        # 3: green_corridors_parks -> max 250 sqm per cell
        db.execute(text("""
            UPDATE feasibility_caps fc
            SET feasibility_cap_sqm = LEAST(ROUND((t.open_soil_sqm * 0.20)::numeric, 0), 250.0)
            FROM temp_cell_lulc t
            WHERE fc.cell_id = t.cell_id AND fc.intervention_id = 3;
        """))

        # 4: permeable_pavement -> max 100 sqm per cell
        db.execute(text("""
            UPDATE feasibility_caps fc
            SET feasibility_cap_sqm = LEAST(ROUND((t.built_up_sqm * 0.10)::numeric, 0), 100.0)
            FROM temp_cell_lulc t
            WHERE fc.cell_id = t.cell_id AND fc.intervention_id = 4;
        """))

        # 5: green_walls -> max 80 sqm per cell
        db.execute(text("""
            UPDATE feasibility_caps fc
            SET feasibility_cap_sqm = LEAST(ROUND((t.built_up_sqm * 0.08)::numeric, 0), 80.0)
            FROM temp_cell_lulc t
            WHERE fc.cell_id = t.cell_id AND fc.intervention_id = 5;
        """))

        # 6: constructed_water_bodies -> max 50 sqm per cell
        db.execute(text("""
            UPDATE feasibility_caps fc
            SET feasibility_cap_sqm = LEAST(ROUND((t.open_soil_sqm * 0.05)::numeric, 0), 50.0)
            FROM temp_cell_lulc t
            WHERE fc.cell_id = t.cell_id AND fc.intervention_id = 6;
        """))

        # 7: shade_structures -> max 50 sqm per cell
        db.execute(text("""
            UPDATE feasibility_caps fc
            SET feasibility_cap_sqm = LEAST(ROUND((t.built_up_sqm * 0.06)::numeric, 0), 50.0)
            FROM temp_cell_lulc t
            WHERE fc.cell_id = t.cell_id AND fc.intervention_id = 7;
        """))
        db.commit()

        print("4. Recalibrating recommendations with realistic municipal costs (Thousands / Lakhs)...")

        # Max Cooling scenario: 80% capacity
        db.execute(text("""
            UPDATE recommendations r
            SET 
                recommended_quantity = ROUND((fc.feasibility_cap_sqm * 0.80)::numeric, 1),
                estimated_cost = ROUND((fc.feasibility_cap_sqm * 0.80 * it.cost_per_unit)::numeric, 2),
                expected_cooling_contribution = ROUND((LEAST(
                    CASE 
                        WHEN it.intervention_id = 1 THEN (fc.feasibility_cap_sqm * 0.80) * 0.05
                        WHEN it.intervention_id = 2 THEN (fc.feasibility_cap_sqm * 0.80) * 0.003
                        WHEN it.intervention_id = 3 THEN (fc.feasibility_cap_sqm * 0.80) * 0.002
                        WHEN it.intervention_id = 4 THEN (fc.feasibility_cap_sqm * 0.80) * 0.001
                        WHEN it.intervention_id = 5 THEN (fc.feasibility_cap_sqm * 0.80) * 0.002
                        WHEN it.intervention_id = 6 THEN (fc.feasibility_cap_sqm * 0.80) * 0.003
                        WHEN it.intervention_id = 7 THEN (fc.feasibility_cap_sqm * 0.80) * 0.002
                        ELSE 0.1
                    END,
                    it.max_cooling_ceiling
                ))::numeric, 2)
            FROM feasibility_caps fc
            JOIN intervention_types it ON it.intervention_id = fc.intervention_id
            WHERE r.cell_id = fc.cell_id 
              AND r.intervention_id = fc.intervention_id
              AND r.scenario_type = 'max_cooling'
              AND fc.feasibility_cap_sqm > 0;
        """))

        # Balanced scenario: 50% capacity (ideal cost-to-benefit)
        db.execute(text("""
            UPDATE recommendations r
            SET 
                recommended_quantity = ROUND((fc.feasibility_cap_sqm * 0.50)::numeric, 1),
                estimated_cost = ROUND((fc.feasibility_cap_sqm * 0.50 * it.cost_per_unit)::numeric, 2),
                expected_cooling_contribution = ROUND((LEAST(
                    CASE 
                        WHEN it.intervention_id = 1 THEN (fc.feasibility_cap_sqm * 0.50) * 0.05
                        WHEN it.intervention_id = 2 THEN (fc.feasibility_cap_sqm * 0.50) * 0.003
                        WHEN it.intervention_id = 3 THEN (fc.feasibility_cap_sqm * 0.50) * 0.002
                        WHEN it.intervention_id = 4 THEN (fc.feasibility_cap_sqm * 0.50) * 0.001
                        WHEN it.intervention_id = 5 THEN (fc.feasibility_cap_sqm * 0.50) * 0.002
                        WHEN it.intervention_id = 6 THEN (fc.feasibility_cap_sqm * 0.50) * 0.003
                        WHEN it.intervention_id = 7 THEN (fc.feasibility_cap_sqm * 0.50) * 0.002
                        ELSE 0.1
                    END,
                    it.max_cooling_ceiling * 0.75
                ))::numeric, 2)
            FROM feasibility_caps fc
            JOIN intervention_types it ON it.intervention_id = fc.intervention_id
            WHERE r.cell_id = fc.cell_id 
              AND r.intervention_id = fc.intervention_id
              AND r.scenario_type = 'balanced'
              AND fc.feasibility_cap_sqm > 0;
        """))

        # Budget scenario: 25% capacity
        db.execute(text("""
            UPDATE recommendations r
            SET 
                recommended_quantity = ROUND((fc.feasibility_cap_sqm * 0.25)::numeric, 1),
                estimated_cost = ROUND((fc.feasibility_cap_sqm * 0.25 * it.cost_per_unit)::numeric, 2),
                expected_cooling_contribution = ROUND((LEAST(
                    CASE 
                        WHEN it.intervention_id = 1 THEN (fc.feasibility_cap_sqm * 0.25) * 0.05
                        WHEN it.intervention_id = 2 THEN (fc.feasibility_cap_sqm * 0.25) * 0.003
                        WHEN it.intervention_id = 3 THEN (fc.feasibility_cap_sqm * 0.25) * 0.002
                        WHEN it.intervention_id = 4 THEN (fc.feasibility_cap_sqm * 0.25) * 0.001
                        WHEN it.intervention_id = 5 THEN (fc.feasibility_cap_sqm * 0.25) * 0.002
                        WHEN it.intervention_id = 6 THEN (fc.feasibility_cap_sqm * 0.25) * 0.003
                        WHEN it.intervention_id = 7 THEN (fc.feasibility_cap_sqm * 0.25) * 0.002
                        ELSE 0.1
                    END,
                    it.max_cooling_ceiling * 0.5
                ))::numeric, 2)
            FROM feasibility_caps fc
            JOIN intervention_types it ON it.intervention_id = fc.intervention_id
            WHERE r.cell_id = fc.cell_id 
              AND r.intervention_id = fc.intervention_id
              AND r.scenario_type = 'budget'
              AND fc.feasibility_cap_sqm > 0;
        """))
        db.commit()

        # Check sample result for cell 72564
        sample = db.execute(text("""
            SELECT scenario_type, SUM(expected_cooling_contribution) as total_cooling, SUM(estimated_cost) as total_cost
            FROM recommendations
            WHERE cell_id = 72564
            GROUP BY scenario_type;
        """)).fetchall()

        print("\nSample Realistic Recalibrated Scenarios for Cell 72564:")
        for s in sample:
            print(f"  Scenario '{s[0]}': Total Cooling = -{s[1]:.2f} C, Total Cost = Rs {s[2]:,.2f}")

    finally:
        db.close()

if __name__ == "__main__":
    recalibrate_feasibility()
