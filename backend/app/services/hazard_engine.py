import logging

from backend.app.models.domain import HazardAssessment, HazardLevel

logger = logging.getLogger(__name__)


class HazardEngine:
    """Evaluates UK Met Office high-resolution weather metrics against summit ridge

    safety thresholds and produces actionable mountain hazard warnings.
    """

    @staticmethod
    def calculate_cloud_base(
        elevation: float,
        temperature: float | None,
        dew_point: float | None,
        reported_cloud_base: float | None = None,
    ) -> float | None:
        """Calculates estimated cloud base height (meters AMSL).

        Uses reported cloud base if present, otherwise computes via the Lawrence
        dew-point depression formula: AMSL = elevation + (T - Td) * 125m.
        """
        if reported_cloud_base is not None and reported_cloud_base > 0:
            return reported_cloud_base

        if temperature is not None and dew_point is not None:
            depression = max(0.0, temperature - dew_point)
            agl_base = depression * 125.0  # Approx 125m per 1°C depression
            return round(elevation + agl_base, 1)

        return None

    @classmethod
    def evaluate(
        cls,
        summit_elevation: float,
        summit_gust: float | None,
        summit_wind_speed: float | None,
        summit_temp: float | None,
        summit_apparent_temp: float | None,
        freezing_level: float | None,
        precip_probability: float | None,
        cloud_cover_low: float | None,
        cloud_base: float | None,
    ) -> HazardAssessment:
        """Evaluates raw summit meteorological conditions against strict mountain safety rules."""
        reasons: list[str] = []
        is_red = False
        is_amber = False

        wind_hazard = False
        icing_hazard = False
        visibility_hazard = False
        chill_hazard = False

        # Safe defaults for partial / null data
        gust = summit_gust if summit_gust is not None else (summit_wind_speed or 0.0)
        sustained = summit_wind_speed if summit_wind_speed is not None else 0.0
        app_temp = summit_apparent_temp if summit_apparent_temp is not None else (summit_temp or 5.0)
        precip_prob = precip_probability if precip_probability is not None else 0.0
        low_cloud = cloud_cover_low if cloud_cover_low is not None else 0.0

        # ======================================================================
        # RED (Severe Hazard) Rules
        # ======================================================================

        # 1. Summit wind gust >= 40 mph (gale force on exposed ridges)
        if gust >= 40.0:
            is_red = True
            wind_hazard = True
            reasons.append(f"Severe gale: Summit wind gusts reaching {gust:.0f} mph (>= 40 mph threshold).")

        # 2. Freezing level <= Summit Elevation AND precipitation probability >= 40%
        # (imminent icing/rime/verglas conditions)
        if freezing_level is not None and freezing_level <= summit_elevation and precip_prob >= 40.0:
            is_red = True
            icing_hazard = True
            reasons.append(
                f"Imminent icing & verglas: Freezing level ({freezing_level:.0f}m) sits at/below "
                f"summit ({summit_elevation:.0f}m) with {precip_prob:.0f}% precipitation risk."
            )

        # 3. Sustained summit wind >= 30 mph with apparent temperature <= -5°C
        if sustained >= 30.0 and app_temp <= -5.0:
            is_red = True
            chill_hazard = True
            reasons.append(
                f"Severe wind chill: Sustained winds of {sustained:.0f} mph with apparent "
                f"temperature feeling like {app_temp:.1f}°C (<= -5°C threshold)."
            )

        if is_red:
            return HazardAssessment(
                level=HazardLevel.RED,
                reasons=reasons,
                wind_hazard=wind_hazard,
                icing_hazard=icing_hazard,
                visibility_hazard=visibility_hazard,
                chill_hazard=chill_hazard,
            )

        # ======================================================================
        # AMBER (Moderate Hazard / Technical Caution) Rules
        # ======================================================================

        # 1. Summit wind gust between 28 mph and 39 mph
        if 28.0 <= gust <= 39.0:
            is_amber = True
            wind_hazard = True
            reasons.append(f"Strong buffeting: Summit wind gusts between {gust:.0f} mph (28-39 mph caution).")

        # 2. Low cloud cover >= 80% with cloud base below summit elevation
        # (persistent clag / low visibility requiring navigation)
        if low_cloud >= 80.0 and cloud_base is not None and cloud_base < summit_elevation:
            is_amber = True
            visibility_hazard = True
            reasons.append(
                f"Dense summit clag: Low cloud cover ({low_cloud:.0f}%) capping the summit. "
                f"Estimated cloud base ({cloud_base:.0f}m) sits below summit ({summit_elevation:.0f}m)."
            )

        # 3. Apparent temperature on summit <= 0°C
        if app_temp <= 0.0:
            is_amber = True
            chill_hazard = True
            reasons.append(f"Freezing apparent temperature: Summit feels like {app_temp:.1f}°C (<= 0°C threshold).")

        if is_amber:
            return HazardAssessment(
                level=HazardLevel.AMBER,
                reasons=reasons,
                wind_hazard=wind_hazard,
                icing_hazard=icing_hazard,
                visibility_hazard=visibility_hazard,
                chill_hazard=chill_hazard,
            )

        # ======================================================================
        # GREEN (Benign / Favourable)
        # ======================================================================
        reasons.append(
            f"Favourable summit conditions: Wind gusts {gust:.0f} mph (< 28 mph), "
            f"no severe wind chill ({app_temp:.1f}°C), and clear ridge visibility."
        )

        return HazardAssessment(
            level=HazardLevel.GREEN,
            reasons=reasons,
            wind_hazard=False,
            icing_hazard=False,
            visibility_hazard=False,
            chill_hazard=False,
        )


hazard_engine = HazardEngine()
