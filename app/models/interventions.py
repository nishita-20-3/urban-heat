from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from app.database import Base


class InterventionType(Base):
    __tablename__ = "intervention_types"

    intervention_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    unit = Column(String(30), nullable=False)
    cost_per_unit = Column(Float, nullable=False)
    cooling_coefficient = Column(Float, nullable=False)
    cooling_unit = Column(String(50), nullable=False)
    applicable_lulc_classes = Column(ARRAY(String(200)))
    data_confidence = Column(String(20), nullable=False)
    notes = Column(Text)
    coverage_ratio = Column(Float, nullable=False)
    max_cooling_ceiling = Column(Float)

    feasibility_caps = relationship("FeasibilityCap", back_populates="intervention_type")
    recommendations = relationship("Recommendation", back_populates="intervention_type")


class FeasibilityCap(Base):
    __tablename__ = "feasibility_caps"

    cap_id = Column(Integer, primary_key=True, autoincrement=True)
    cell_id = Column(Integer, ForeignKey("grid_cells.cell_id"), nullable=False, index=True)
    intervention_id = Column(Integer, ForeignKey("intervention_types.intervention_id"), nullable=False, index=True)
    feasibility_cap_sqm = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("cell_id", "intervention_id", name="uq_feasibility_cell_intervention"),
    )

    grid_cell = relationship("GridCell", back_populates="feasibility_caps")
    intervention_type = relationship("InterventionType", back_populates="feasibility_caps")


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(Integer, primary_key=True, autoincrement=True)
    cell_id = Column(Integer, ForeignKey("grid_cells.cell_id"), nullable=False, index=True)
    scenario_type = Column(String(20))
    intervention_id = Column(Integer, ForeignKey("intervention_types.intervention_id"), index=True)
    recommended_quantity = Column(Float)
    expected_cooling_contribution = Column(Float)
    estimated_cost = Column(Float)
    created_at = Column(DateTime, server_default=func.now())

    grid_cell = relationship("GridCell", back_populates="recommendations")
    intervention_type = relationship("InterventionType", back_populates="recommendations")
