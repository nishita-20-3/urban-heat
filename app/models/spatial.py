from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Float, func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.database import Base


class City(Base):
    __tablename__ = "cities"

    city_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    boundary = Column(Geometry("MultiPolygon", srid=4326), nullable=False)
    is_prototype = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    grid_cells = relationship("GridCell", back_populates="city", cascade="all, delete-orphan")
    zones = relationship("Zone", back_populates="city", cascade="all, delete-orphan")
    planning_areas = relationship("PlanningArea", back_populates="city", cascade="all, delete-orphan")


class Zone(Base):
    __tablename__ = "zones"

    zone_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey("cities.city_id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)
    description = Column(Text)
    color = Column(String(20))
    geom = Column(Geometry("MultiPolygon", srid=4326), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    city = relationship("City", back_populates="zones")
    grid_cells = relationship("GridCell", back_populates="zone")
    planning_areas = relationship("PlanningArea", back_populates="zone", cascade="all, delete-orphan")


class PlanningArea(Base):
    __tablename__ = "planning_areas"

    area_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    zone_id = Column(Integer, ForeignKey("zones.zone_id"), nullable=False, index=True)
    city_id = Column(Integer, ForeignKey("cities.city_id"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    code = Column(String(30), nullable=False)
    area_type = Column(String(50), nullable=False)
    is_hotspot = Column(Boolean, default=False, nullable=False)
    description = Column(Text)
    building_rooftop_sqm = Column(Float, nullable=False, default=0.0)
    road_paved_sqm = Column(Float, nullable=False, default=0.0)
    open_ground_sqm = Column(Float, nullable=False, default=0.0)
    water_body_sqm = Column(Float, nullable=False, default=0.0)
    existing_tree_cover_sqm = Column(Float, nullable=False, default=0.0)
    avg_lst_summer = Column(Float, nullable=False, default=42.0)
    peak_lst_summer = Column(Float, nullable=False, default=46.0)
    geom = Column(Geometry("MultiPolygon", srid=4326))
    created_at = Column(DateTime, server_default=func.now())

    city = relationship("City", back_populates="planning_areas")
    zone = relationship("Zone", back_populates="planning_areas")
    grid_cells = relationship("GridCell", back_populates="planning_area")


class GridCell(Base):
    __tablename__ = "grid_cells"

    cell_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey("cities.city_id"), nullable=False, index=True)
    zone_id = Column(Integer, ForeignKey("zones.zone_id"), nullable=True, index=True)
    area_id = Column(Integer, ForeignKey("planning_areas.area_id"), nullable=True, index=True)
    geom = Column(Geometry("Polygon", srid=4326), nullable=False)
    centroid = Column(Geometry("Point", srid=4326), nullable=False)

    city = relationship("City", back_populates="grid_cells")
    zone = relationship("Zone", back_populates="grid_cells")
    planning_area = relationship("PlanningArea", back_populates="grid_cells")
    satellite_observations = relationship("SatelliteObservation", back_populates="grid_cell")
    lulc_classifications = relationship("LulcClassification", back_populates="grid_cell")
    heat_predictions = relationship("HeatPrediction", back_populates="grid_cell")
    feasibility_caps = relationship("FeasibilityCap", back_populates="grid_cell")
    recommendations = relationship("Recommendation", back_populates="grid_cell")
