from backend.app.models.domain import HazardLevel
from backend.app.services.hazard_engine import HazardEngine, hazard_engine


class TestHazardEngine:
    def test_wind_gust_threshold_amber_vs_red(self):
        """Test summit wind gust at 39 mph (Amber) vs 40 mph (Red)."""
        # 39 mph -> Amber
        amber_eval = hazard_engine.evaluate(
            summit_elevation=978.0,
            summit_gust=39.0,
            summit_wind_speed=20.0,
            summit_temp=8.0,
            summit_apparent_temp=5.0,
            freezing_level=1500.0,
            precip_probability=10.0,
            cloud_cover_low=30.0,
            cloud_base=1500.0,
        )
        assert amber_eval.level == HazardLevel.AMBER
        assert amber_eval.wind_hazard is True
        assert any("28-39 mph" in r for r in amber_eval.reasons)

        # 40 mph -> Red
        red_eval = hazard_engine.evaluate(
            summit_elevation=978.0,
            summit_gust=40.0,
            summit_wind_speed=25.0,
            summit_temp=8.0,
            summit_apparent_temp=5.0,
            freezing_level=1500.0,
            precip_probability=10.0,
            cloud_cover_low=30.0,
            cloud_base=1500.0,
        )
        assert red_eval.level == HazardLevel.RED
        assert red_eval.wind_hazard is True
        assert any("Severe gale" in r for r in red_eval.reasons)

    def test_cloud_clag_above_vs_below_summit(self):
        """Test cloud clag when low cloud base sits at 1,050m vs Scafell at 978m."""
        # Cloud base at 1050m > 978m summit -> Green (clear ridge)
        green_eval = hazard_engine.evaluate(
            summit_elevation=978.0,
            summit_gust=20.0,
            summit_wind_speed=15.0,
            summit_temp=7.0,
            summit_apparent_temp=4.0,
            freezing_level=1600.0,
            precip_probability=10.0,
            cloud_cover_low=90.0,
            cloud_base=1050.0,
        )
        assert green_eval.level == HazardLevel.GREEN
        assert green_eval.visibility_hazard is False

        # Cloud base at 800m < 978m summit with 85% low cloud -> Amber (dense clag)
        amber_eval = hazard_engine.evaluate(
            summit_elevation=978.0,
            summit_gust=20.0,
            summit_wind_speed=15.0,
            summit_temp=7.0,
            summit_apparent_temp=4.0,
            freezing_level=1600.0,
            precip_probability=10.0,
            cloud_cover_low=85.0,
            cloud_base=800.0,
        )
        assert amber_eval.level == HazardLevel.AMBER
        assert amber_eval.visibility_hazard is True
        assert any("Dense summit clag" in r for r in amber_eval.reasons)

    def test_icing_conditions_flag(self):
        """Test icing condition flag triggered when freezing level is 800m and precip is 50%."""
        eval_result = hazard_engine.evaluate(
            summit_elevation=978.0,
            summit_gust=25.0,
            summit_wind_speed=18.0,
            summit_temp=0.0,
            summit_apparent_temp=-2.0,
            freezing_level=800.0,  # <= 978m
            precip_probability=50.0,  # >= 40%
            cloud_cover_low=50.0,
            cloud_base=1200.0,
        )
        assert eval_result.level == HazardLevel.RED
        assert eval_result.icing_hazard is True
        assert any("Imminent icing & verglas" in r for r in eval_result.reasons)

    def test_sustained_wind_and_wind_chill_red(self):
        """Test sustained summit wind >= 30 mph with apparent temperature <= -5°C."""
        eval_result = hazard_engine.evaluate(
            summit_elevation=900.0,
            summit_gust=35.0,
            summit_wind_speed=32.0,  # >= 30 mph
            summit_temp=-2.0,
            summit_apparent_temp=-7.0,  # <= -5°C
            freezing_level=1200.0,
            precip_probability=10.0,
            cloud_cover_low=30.0,
            cloud_base=1500.0,
        )
        assert eval_result.level == HazardLevel.RED
        assert eval_result.chill_hazard is True
        assert any("Severe wind chill" in r for r in eval_result.reasons)

    def test_apparent_temp_amber(self):
        """Test apparent temperature <= 0°C triggers Amber."""
        eval_result = hazard_engine.evaluate(
            summit_elevation=900.0,
            summit_gust=20.0,
            summit_wind_speed=15.0,
            summit_temp=2.0,
            summit_apparent_temp=-0.5,  # <= 0°C
            freezing_level=1500.0,
            precip_probability=15.0,
            cloud_cover_low=20.0,
            cloud_base=1500.0,
        )
        assert eval_result.level == HazardLevel.AMBER
        assert eval_result.chill_hazard is True
        assert any("Freezing apparent temperature" in r for r in eval_result.reasons)

    def test_benign_green_conditions(self):
        """Test summit wind gusts < 28 mph, cloud base verified above summit elevation, no severe wind chill."""
        eval_result = hazard_engine.evaluate(
            summit_elevation=900.0,
            summit_gust=18.0,
            summit_wind_speed=12.0,
            summit_temp=12.0,
            summit_apparent_temp=10.0,
            freezing_level=2500.0,
            precip_probability=5.0,
            cloud_cover_low=20.0,
            cloud_base=1800.0,
        )
        assert eval_result.level == HazardLevel.GREEN
        assert eval_result.wind_hazard is False
        assert eval_result.icing_hazard is False
        assert eval_result.visibility_hazard is False
        assert eval_result.chill_hazard is False
        assert any("Favourable summit conditions" in r for r in eval_result.reasons)

    def test_fallback_handling_with_null_and_partial_readings(self):
        """Test fallback handling when UKMO data contains null or partial readings."""
        eval_result = hazard_engine.evaluate(
            summit_elevation=978.0,
            summit_gust=None,
            summit_wind_speed=None,
            summit_temp=None,
            summit_apparent_temp=None,
            freezing_level=None,
            precip_probability=None,
            cloud_cover_low=None,
            cloud_base=None,
        )
        # Should gracefully return Green without raising an exception
        assert eval_result.level == HazardLevel.GREEN
        assert len(eval_result.reasons) > 0

    def test_cloud_base_calculation(self):
        """Test calculation of cloud base via dew-point depression formula."""
        # 100m elevation, Temp 12°C, Dew point 8°C -> 4°C depression * 125m = 500m + 100m = 600m
        cb = HazardEngine.calculate_cloud_base(
            elevation=100.0,
            temperature=12.0,
            dew_point=8.0,
        )
        assert cb == 600.0

        # With reported cloud base
        cb_rep = HazardEngine.calculate_cloud_base(
            elevation=100.0,
            temperature=12.0,
            dew_point=8.0,
            reported_cloud_base=750.0,
        )
        assert cb_rep == 750.0

        # Missing temperature or dew point
        cb_none = HazardEngine.calculate_cloud_base(
            elevation=100.0,
            temperature=None,
            dew_point=8.0,
        )
        assert cb_none is None
