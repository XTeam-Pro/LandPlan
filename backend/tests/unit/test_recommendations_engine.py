"""Tests for Recommendations Engine"""

import pytest
from sqlalchemy.orm import Session

from app.bounded_contexts.recommendations.engine import (
    RecommendationEngine,
    Priority,
)
from app.models import Land, LandFeature, Source, Region
from datetime import datetime


class TestRecommendationEngine:
    """Tests for the rule-based recommendation engine"""

    @pytest.fixture
    def setup_data(self, db_session: Session):
        """Setup test data"""
        # Create region
        region = Region(name="Test Region", slug="test-region")
        db_session.add(region)
        db_session.flush()

        # Create source
        source = Source(type="private", name="Test Source")
        db_session.add(source)
        db_session.flush()

        return region, source

    def test_recommendation_water_missing(self, db_session: Session, setup_data):
        """Test: Water missing → water services recommended"""
        region, source = setup_data

        land = Land(
            title="Test Land",
            address="Test Address",
            latitude=55.0,
            longitude=37.0,
            source_id=source.id,
            region_id=region.id,
        )
        db_session.add(land)
        db_session.flush()

        features = LandFeature(
            land_id=land.id,
            has_water=False,  # NO WATER
            boundaries_defined=True,
        )
        db_session.add(features)
        db_session.commit()

        # Get recommendations
        result = RecommendationEngine.get_recommendations(land, features)

        # Should recommend water services
        assert len(result["services"]) > 0
        water_services = [s for s in result["services"]
                         if "water" in s.service_slug.lower()]
        assert len(water_services) >= 3
        assert water_services[0].priority == Priority.CRITICAL

    def test_recommendation_boundaries_missing(self, db_session: Session, setup_data):
        """Test: Boundaries missing → cadastre services recommended"""
        region, source = setup_data

        land = Land(
            title="Test Land",
            address="Test Address",
            latitude=55.0,
            longitude=37.0,
            source_id=source.id,
            region_id=region.id,
        )
        db_session.add(land)
        db_session.flush()

        features = LandFeature(
            land_id=land.id,
            has_water=True,
            boundaries_defined=False,  # NO BOUNDARIES
        )
        db_session.add(features)
        db_session.commit()

        result = RecommendationEngine.get_recommendations(land, features)

        # Should recommend cadastral services
        cadastral_services = [s for s in result["services"]
                             if "cadastral" in s.service_slug.lower()
                             or "boundary" in s.service_slug.lower()]
        assert len(cadastral_services) > 0
        assert cadastral_services[0].priority == Priority.CRITICAL

    def test_recommendation_purchase_deal(self, db_session: Session, setup_data):
        """Test: Purchase deal → legal services recommended"""
        region, source = setup_data

        land = Land(
            title="Test Land",
            address="Test Address",
            latitude=55.0,
            longitude=37.0,
            source_id=source.id,
            region_id=region.id,
            deal_type="purchase",  # PURCHASE
        )
        db_session.add(land)
        db_session.flush()

        features = LandFeature(
            land_id=land.id,
            has_water=True,
            boundaries_defined=True,
        )
        db_session.add(features)
        db_session.commit()

        result = RecommendationEngine.get_recommendations(land, features)

        # Should recommend legal services
        legal_services = [s for s in result["services"]
                         if "legal" in s.service_slug.lower()
                         or "purchase" in s.service_slug.lower()]
        assert len(legal_services) > 0
        assert legal_services[0].priority == Priority.CRITICAL

    def test_recommendation_not_build_ready(self, db_session: Session, setup_data):
        """Test: Not build ready → geological services recommended"""
        region, source = setup_data

        land = Land(
            title="Test Land",
            address="Test Address",
            latitude=55.0,
            longitude=37.0,
            source_id=source.id,
            region_id=region.id,
        )
        db_session.add(land)
        db_session.flush()

        features = LandFeature(
            land_id=land.id,
            has_water=True,
            boundaries_defined=True,
            build_ready=False,  # NOT READY
        )
        db_session.add(features)
        db_session.commit()

        result = RecommendationEngine.get_recommendations(land, features)

        # Should recommend geological services
        geo_services = [s for s in result["services"]
                       if "geological" in s.service_slug.lower()
                       or "soil" in s.service_slug.lower()]
        assert len(geo_services) > 0
        assert geo_services[0].priority == Priority.RECOMMENDED

    def test_complex_scenario(self, db_session: Session, setup_data):
        """Test: Complex scenario - multiple issues"""
        region, source = setup_data

        # Land with multiple problems
        land = Land(
            title="Complex Test Land",
            address="Complex Address",
            latitude=55.0,
            longitude=37.0,
            source_id=source.id,
            region_id=region.id,
            deal_type="purchase",
        )
        db_session.add(land)
        db_session.flush()

        features = LandFeature(
            land_id=land.id,
            has_water=False,
            has_electricity=False,
            has_gas=False,
            boundaries_defined=False,
            build_ready=False,
        )
        db_session.add(features)
        db_session.commit()

        result = RecommendationEngine.get_recommendations(land, features)

        # Should recommend many services
        assert result["total_critical"] > 2
        assert result["total_recommended"] > 2

        # Check priority ordering
        services = result["services"]
        for i, service in enumerate(services):
            if i > 0:
                current_priority = self._get_priority_value(service.priority)
                prev_priority = self._get_priority_value(services[i - 1].priority)
                assert current_priority >= prev_priority

    def test_summary_generation(self, db_session: Session, setup_data):
        """Test: Summary text is generated correctly"""
        region, source = setup_data

        land = Land(
            title="Test Land",
            address="Test Address",
            latitude=55.0,
            longitude=37.0,
            source_id=source.id,
            region_id=region.id,
        )
        db_session.add(land)
        db_session.flush()

        features = LandFeature(
            land_id=land.id,
            has_water=False,
            boundaries_defined=False,
        )
        db_session.add(features)
        db_session.commit()

        result = RecommendationEngine.get_recommendations(land, features)

        # Should have summary
        assert "summary" in result
        assert len(result["summary"]) > 0
        assert "Обязательно" in result["summary"] or "Рекомендуется" in result["summary"]

    def test_service_ordering(self, db_session: Session, setup_data):
        """Test: Services are ordered correctly"""
        region, source = setup_data

        land = Land(
            title="Test Land",
            address="Test Address",
            latitude=55.0,
            longitude=37.0,
            source_id=source.id,
            region_id=region.id,
        )
        db_session.add(land)
        db_session.flush()

        features = LandFeature(land_id=land.id)
        db_session.add(features)
        db_session.commit()

        result = RecommendationEngine.get_recommendations(land, features)

        services = result["services"]

        # Check that critical comes before recommended
        critical_indices = [i for i, s in enumerate(services)
                           if s.priority == Priority.CRITICAL]
        recommended_indices = [i for i, s in enumerate(services)
                              if s.priority == Priority.RECOMMENDED]

        if critical_indices and recommended_indices:
            assert max(critical_indices) <= min(recommended_indices)

    @staticmethod
    def _get_priority_value(priority_str: str) -> int:
        """Convert priority string to numeric value for comparison"""
        priority_map = {
            Priority.CRITICAL: 1,
            Priority.RECOMMENDED: 2,
            Priority.OPTIONAL: 3,
        }
        return priority_map.get(priority_str, 999)
