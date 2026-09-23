import json
import sqlite3
import pytest
from datetime import date
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from fastapi.testclient import TestClient

# Register sqlite3 adapters for list and dict so SQLite can bind JSON/ARRAY fields
sqlite3.register_adapter(list, json.dumps)
sqlite3.register_adapter(dict, json.dumps)

from app.main import app
from app.database import Base, get_db
from app.models import (
    City,
    Zone,
    GridCell,
    SatelliteObservation,
    LulcClassification,
    HeatPrediction,
    InterventionType,
    FeasibilityCap,
    Recommendation,
)

# Custom SQLite compilation rules for PostgreSQL specific types
@compiles(JSONB, "sqlite")
def compile_jsonb(element, compiler, **kw):
    return "TEXT"


@compiles(ARRAY, "sqlite")
def compile_array(element, compiler, **kw):
    return "TEXT"


# Create test SQLite engine with StaticPool so all sessions share the same in-memory DB
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def register_sqlite_spatial_functions(dbapi_conn, record):
    """
    Register SQLite mock functions for PostGIS / SpatiaLite functions.
    """
    def dummy(*args):
        return 1

    def dummy_none(*args):
        return None

    def passthrough(*args):
        return args[0] if args else None

    def st_as_geojson(geom):
        if geom is None:
            return None
        return json.dumps({
            "type": "Polygon",
            "coordinates": [
                [[72.81, 21.17], [72.82, 21.17], [72.82, 21.18], [72.81, 21.18], [72.81, 21.17]]
            ]
        })

    def st_intersects(geom, envelope):
        if envelope == "envelope_match":
            return 1
        elif envelope == "envelope_no_match":
            return 0
        return 1

    def st_make_envelope(min_x, min_y, max_x, max_y, srid):
        if min_x > 80.0:
            return "envelope_no_match"
        return "envelope_match"

    # SpatiaLite / PostGIS functions
    dbapi_conn.create_function("RecoverGeometryColumn", -1, dummy)
    dbapi_conn.create_function("InitSpatialMetaData", -1, dummy)
    dbapi_conn.create_function("AddGeometryColumn", -1, dummy)
    dbapi_conn.create_function("DiscardGeometryColumn", -1, dummy)
    dbapi_conn.create_function("CreateSpatialIndex", -1, dummy)
    dbapi_conn.create_function("DisableSpatialIndex", -1, dummy)
    dbapi_conn.create_function("CheckSpatialIndex", -1, dummy_none)
    dbapi_conn.create_function("DropGeometryColumn", -1, dummy)
    dbapi_conn.create_function("DropSpatialIndex", -1, dummy)
    
    dbapi_conn.create_function("GeomFromEWKT", -1, passthrough)
    dbapi_conn.create_function("GeomFromText", -1, passthrough)
    dbapi_conn.create_function("ST_GeomFromEWKT", -1, passthrough)
    dbapi_conn.create_function("ST_GeomFromText", -1, passthrough)
    dbapi_conn.create_function("AsEWKT", -1, passthrough)
    dbapi_conn.create_function("ST_AsEWKT", -1, passthrough)
    dbapi_conn.create_function("AsBinary", -1, passthrough)
    dbapi_conn.create_function("ST_AsBinary", -1, passthrough)
    dbapi_conn.create_function("AsEWKB", -1, passthrough)
    dbapi_conn.create_function("ST_AsEWKB", -1, passthrough)

    dbapi_conn.create_function("AsGeoJSON", -1, st_as_geojson)
    dbapi_conn.create_function("ST_AsGeoJSON", -1, st_as_geojson)
    dbapi_conn.create_function("ST_Intersects", 2, st_intersects)
    dbapi_conn.create_function("ST_MakeEnvelope", 5, st_make_envelope)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db_session():
    """
    Fresh database session for each test.
    """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session: Session):
    """
    FastAPI TestClient with overridden get_db dependency.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def seed_data(db_session: Session):
    """
    Seed initial test data matching Surat test case.
    """
    # Clean existing data before seeding
    db_session.query(Recommendation).delete()
    db_session.query(FeasibilityCap).delete()
    db_session.query(InterventionType).delete()
    db_session.query(HeatPrediction).delete()
    db_session.query(LulcClassification).delete()
    db_session.query(SatelliteObservation).delete()
    db_session.query(GridCell).delete()
    db_session.query(Zone).delete()
    db_session.query(City).delete()
    db_session.commit()

    # 1. Seed City
    city = City(
        city_id=1,
        name="Surat",
        state="Gujarat",
        boundary="SRID=4326;MULTIPOLYGON(((72.7 21.1, 72.9 21.1, 72.9 21.3, 72.7 21.3, 72.7 21.1)))",
        is_prototype=True,
    )
    db_session.add(city)
    db_session.commit()

    # 1b. Seed Zone
    zone1 = Zone(
        zone_id=1,
        city_id=1,
        name="Central Zone",
        code="CZ-01",
        description="Old walled city",
        color="#E8543E",
        geom="SRID=4326;MULTIPOLYGON(((72.81 21.17, 72.84 21.17, 72.84 21.20, 72.81 21.20, 72.81 21.17)))",
    )
    db_session.add(zone1)
    db_session.commit()

    # 2. Seed Grid Cells
    cell1 = GridCell(
        cell_id=101,
        city_id=1,
        zone_id=1,
        geom="SRID=4326;POLYGON((72.81 21.17, 72.82 21.17, 72.82 21.18, 72.81 21.18, 72.81 21.17))",
        centroid="SRID=4326;POINT(72.815 21.175)",
    )
    cell2 = GridCell(
        cell_id=102,
        city_id=1,
        zone_id=1,
        geom="SRID=4326;POLYGON((72.83 21.17, 72.84 21.17, 72.84 21.18, 72.83 21.18, 72.83 21.17))",
        centroid="SRID=4326;POINT(72.835 21.175)",
    )
    db_session.add_all([cell1, cell2])
    db_session.commit()

    # 3. Seed Predictions for Cell 101
    pred_summer = HeatPrediction(
        prediction_id=1,
        cell_id=101,
        season="summer",
        prediction_date=date(2026, 8, 18),
        predicted_lst=45.8,
        actual_lst=46.2,
        cooling_gap=3.5,
        shap_values={
            "base_value": 37.35,
            "ndvi": 0.496,
            "ndbi": 3.071,
            "air_temp": 5.144,
            "humidity": -0.091,
            "wind_speed": -1.093,
            "Built-up_pct": -0.041,
            "Tree cover_pct": 0.422,
        },
        model_version="v1.0.0",
    )
    pred_monsoon = HeatPrediction(
        prediction_id=2,
        cell_id=101,
        season="monsoon",
        prediction_date=date(2026, 8, 18),
        predicted_lst=33.2,
        actual_lst=None,
        cooling_gap=1.2,
        shap_values={
            "ndvi": -0.2,
            "ndbi": 1.1,
            "air_temp": 2.3,
        },
        model_version="v1.0.0",
    )
    db_session.add_all([pred_summer, pred_monsoon])
    db_session.commit()

    # 4. Seed Intervention Types
    it1 = InterventionType(
        intervention_id=1,
        name="tree_planting",
        unit="per tree",
        cost_per_unit=300.0,
        cooling_coefficient=0.071,
        cooling_unit="deg_C_per_100_trees",
        applicable_lulc_classes=["Built-up", "Barren land"],
        data_confidence="strong",
        notes="Native shade trees recommended",
        coverage_ratio=0.8,
        max_cooling_ceiling=4.5,
    )
    it2 = InterventionType(
        intervention_id=2,
        name="cool_roofing",
        unit="per sqm",
        cost_per_unit=150.0,
        cooling_coefficient=0.045,
        cooling_unit="deg_C_per_1000_sqm",
        applicable_lulc_classes=["Built-up"],
        data_confidence="moderate",
        notes="High-albedo reflective roof coatings",
        coverage_ratio=0.6,
        max_cooling_ceiling=3.0,
    )
    db_session.add_all([it1, it2])
    db_session.commit()

    # 5. Seed Recommendations for Cell 101
    rec1 = Recommendation(
        recommendation_id=1,
        cell_id=101,
        scenario_type="max_cooling",
        intervention_id=1,
        recommended_quantity=42.0,
        expected_cooling_contribution=3.0,
        estimated_cost=12600.0,
    )
    rec2 = Recommendation(
        recommendation_id=2,
        cell_id=101,
        scenario_type="max_cooling",
        intervention_id=2,
        recommended_quantity=500.0,
        expected_cooling_contribution=5.9,
        estimated_cost=4520000.0,
    )
    rec3 = Recommendation(
        recommendation_id=3,
        cell_id=101,
        scenario_type="balanced",
        intervention_id=1,
        recommended_quantity=20.0,
        expected_cooling_contribution=1.5,
        estimated_cost=6000.0,
    )
    db_session.add_all([rec1, rec2, rec3])
    db_session.commit()
