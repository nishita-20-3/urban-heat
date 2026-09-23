from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class HeatPrediction(Base):
    __tablename__ = "heat_predictions"

    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    cell_id = Column(Integer, ForeignKey("grid_cells.cell_id"), nullable=False, index=True)
    season = Column(String(20), nullable=False)
    prediction_date = Column(Date, nullable=False)
    predicted_lst = Column(Float, nullable=False)
    actual_lst = Column(Float)
    cooling_gap = Column(Float)
    shap_values = Column(JSONB)
    model_version = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("cell_id", "season", "model_version", name="uq_heat_pred_cell_season_model"),
    )

    grid_cell = relationship("GridCell", back_populates="heat_predictions")
