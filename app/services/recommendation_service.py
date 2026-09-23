from typing import Dict, List
from collections import defaultdict
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError
from app.services.prediction_service import verify_cell_exists
from app.models.interventions import Recommendation, InterventionType
from app.schemas.recommendation import (
    RecommendationResponse,
    ScenarioDetail,
    InterventionItem,
)


def get_recommendations_for_cell(db: Session, cell_id: int) -> RecommendationResponse:
    """
    Returns recommended interventions for a cell grouped by scenario.
    If the recommendations table does not exist or has no rows for this cell,
    returns 200 OK with an empty 'scenarios' dictionary.
    """
    # 1. Check if cell exists in grid_cells (raises 404 if not found)
    verify_cell_exists(db, cell_id)

    # 2. Check if recommendations table exists in the database
    try:
        inspector = inspect(db.bind)
        if not inspector.has_table("recommendations"):
            return RecommendationResponse(cell_id=cell_id, scenarios={})
    except Exception:
        # If inspector inspection encounters any issue, we proceed to attempt query in try-except
        pass

    # 3. Query recommendations joined with intervention_types
    try:
        rows = (
            db.query(
                Recommendation.scenario_type,
                Recommendation.recommended_quantity,
                Recommendation.expected_cooling_contribution,
                Recommendation.estimated_cost,
                InterventionType.name.label("intervention_name"),
                InterventionType.unit.label("intervention_unit"),
            )
            .join(
                InterventionType,
                Recommendation.intervention_id == InterventionType.intervention_id,
            )
            .filter(Recommendation.cell_id == cell_id)
            .all()
        )
    except (ProgrammingError, SQLAlchemyError):
        # Gracefully handle missing table or query errors
        db.rollback()
        return RecommendationResponse(cell_id=cell_id, scenarios={})

    if not rows:
        return RecommendationResponse(cell_id=cell_id, scenarios={})

    # 4. Group by scenario_type
    grouped_interventions: Dict[str, List[InterventionItem]] = defaultdict(list)
    for row in rows:
        scenario = row.scenario_type or "default"
        grouped_interventions[scenario].append(
            InterventionItem(
                name=row.intervention_name or "unknown",
                quantity=float(row.recommended_quantity or 0.0),
                unit=row.intervention_unit or "",
                cooling_contribution_c=float(row.expected_cooling_contribution or 0.0),
                cost_inr=float(row.estimated_cost or 0.0),
            )
        )

    scenarios: Dict[str, ScenarioDetail] = {}
    for scenario_name, items in grouped_interventions.items():
        total_cooling = sum(item.cooling_contribution_c for item in items)
        total_cost = sum(item.cost_inr for item in items)
        scenarios[scenario_name] = ScenarioDetail(
            total_cooling_c=round(total_cooling, 2),
            total_cost_inr=round(total_cost, 2),
            interventions=items,
        )

    return RecommendationResponse(cell_id=cell_id, scenarios=scenarios)
