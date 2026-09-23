from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class SatelliteObservation(Base):
    __tablename__ = "satellite_observations"

    obs_id = Column(Integer, primary_key=True, autoincrement=True)
    cell_id = Column(Integer, ForeignKey("grid_cells.cell_id"), nullable=False, index=True)
    observation_date = Column(Date, nullable=False)
    source = Column(String(50), nullable=False)
    ndvi = Column(Float)
    ndbi = Column(Float)
    lst = Column(Float)
    air_temp = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)

    __table_args__ = (
        UniqueConstraint("cell_id", "observation_date", "source", name="uq_sat_obs_cell_date_src"),
    )

    grid_cell = relationship("GridCell", back_populates="satellite_observations")


class LulcClassification(Base):
    __tablename__ = "lulc_classification"

    lulc_id = Column(Integer, primary_key=True, autoincrement=True)
    cell_id = Column(Integer, ForeignKey("grid_cells.cell_id"), nullable=False, index=True)
    lulc_class = Column(Integer, nullable=False)
    class_name = Column(String(50), nullable=False)
    pixel_count = Column(Float, nullable=False)
    area_sqm = Column(Float, nullable=False)
    year = Column(Integer, default=2021)

    __table_args__ = (
        UniqueConstraint("cell_id", "year", "lulc_class", name="uq_lulc_cell_year_class"),
    )

    grid_cell = relationship("GridCell", back_populates="lulc_classifications")
