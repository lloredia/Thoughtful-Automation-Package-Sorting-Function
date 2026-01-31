"""
Test suite for the package sorting function.

Coverage strategy:
    1. Core routing — one clean case per stack
    2. Bulky triggers — volume threshold, each single dimension >= 150
    3. Heavy trigger  — mass threshold
    4. Boundary values — exact thresholds (at, just below, just above)
    5. Combined states — heavy+bulky combos that hit REJECTED
    6. Edge cases — zero dimensions, very large values, floats
    7. Error handling — negative values, bad types
"""

import pytest
from sort import sort


# ---------------------------------------------------------------------------
# 1. Core routing — baseline happy path for each stack
# ---------------------------------------------------------------------------
class TestCoreRouting:
    def test_standard_small_light_package(self):
        # 10x10x10 = 1000 cm³, mass 5 kg → neither bulky nor heavy
        assert sort(10, 10, 10, 5) == "STANDARD"

    def test_special_bulky_only(self):
        # Volume = 1,000,000 exactly, mass 10 kg (not heavy)
        assert sort(100, 100, 100, 10) == "SPECIAL"

    def test_special_heavy_only(self):
        # Small package (1000 cm³), mass = 20 kg exactly
        assert sort(10, 10, 10, 20) == "SPECIAL"

    def test_rejected_both_bulky_and_heavy(self):
        # Volume = 1,000,000, mass = 20 kg
        assert sort(100, 100, 100, 20) == "REJECTED"


# ---------------------------------------------------------------------------
# 2. Bulky triggers — each way a package can become bulky
# ---------------------------------------------------------------------------
class TestBulkyByVolume:
    def test_volume_exactly_at_threshold(self):
        # 100 * 100 * 100 = 1,000,000 → bulky
        assert sort(100, 100, 100, 1) == "SPECIAL"

    def test_volume_one_above_threshold(self):
        # 100 * 100 * 100.01 = 1,000,100 → bulky
        assert sort(100, 100, 100.01, 1) == "SPECIAL"

    def test_volume_one_below_threshold(self):
        # 99 * 100 * 100 = 990,000 → NOT bulky (no dim >= 150 either)
        assert sort(99, 100, 100, 1) == "STANDARD"


class TestBulkyBySingleDimension:
    def test_width_exactly_150(self):
        assert sort(150, 1, 1, 1) == "SPECIAL"

    def test_height_exactly_150(self):
        assert sort(1, 150, 1, 1) == "SPECIAL"

    def test_length_exactly_150(self):
        assert sort(1, 1, 150, 1) == "SPECIAL"

    def test_width_just_below_150(self):
        # 149.99 * 1 * 1 = 149.99 cm³ — not bulky by volume or dimension
        assert sort(149.99, 1, 1, 1) == "STANDARD"

    def test_width_above_150_but_small_volume(self):
        # Single long dimension makes it bulky regardless of volume
        assert sort(200, 1, 1, 1) == "SPECIAL"


# ---------------------------------------------------------------------------
# 3. Heavy trigger — mass boundary
# ---------------------------------------------------------------------------
class TestHeavyThreshold:
    def test_mass_exactly_20(self):
        assert sort(1, 1, 1, 20) == "SPECIAL"

    def test_mass_just_below_20(self):
        assert sort(1, 1, 1, 19.99) == "STANDARD"

    def test_mass_well_above_20(self):
        assert sort(1, 1, 1, 100) == "SPECIAL"


# ---------------------------------------------------------------------------
# 4. Boundary value matrix — all thresholds at/around critical points
# ---------------------------------------------------------------------------
class TestBoundaryMatrix:
    """
    Systematically test the four corners of the bulky/heavy space
    at exact threshold values.
    """

    def test_not_bulky_not_heavy(self):
        # Volume < 1M, no dim >= 150, mass < 20
        assert sort(99, 99, 99, 19) == "STANDARD"

    def test_bulky_not_heavy_by_volume(self):
        assert sort(100, 100, 100, 19) == "SPECIAL"

    def test_not_bulky_heavy(self):
        assert sort(99, 99, 99, 20) == "SPECIAL"

    def test_bulky_heavy_by_volume(self):
        assert sort(100, 100, 100, 20) == "REJECTED"

    def test_bulky_heavy_by_dimension(self):
        # Bulky via dimension (not volume), heavy via mass
        assert sort(150, 1, 1, 20) == "REJECTED"

    def test_bulky_by_dimension_and_volume_simultaneously(self):
        # Both triggers active for bulky — still just SPECIAL if not heavy
        assert sort(150, 150, 150, 1) == "SPECIAL"


# ---------------------------------------------------------------------------
# 5. Combined / tricky scenarios
# ---------------------------------------------------------------------------
class TestCombinedScenarios:
    def test_bulky_by_dimension_not_by_volume_heavy(self):
        # dim >= 150 but volume < 1M; mass >= 20 → REJECTED
        assert sort(150, 1, 1, 25) == "REJECTED"

    def test_bulky_by_volume_not_by_dimension_heavy(self):
        # volume >= 1M but all dims < 150; mass >= 20 → REJECTED
        assert sort(100, 100, 100, 50) == "REJECTED"

    def test_multiple_dimensions_over_150(self):
        assert sort(200, 200, 200, 5) == "SPECIAL"

    def test_multiple_dimensions_over_150_and_heavy(self):
        assert sort(200, 200, 200, 30) == "REJECTED"


# ---------------------------------------------------------------------------
# 6. Edge cases — zeros, floats, large values
# ---------------------------------------------------------------------------
class TestEdgeCases:
    def test_all_zeros_except_mass(self):
        # Volume = 0, no dim >= 150, mass 0 → STANDARD
        assert sort(0, 0, 0, 0) == "STANDARD"

    def test_zero_volume_heavy(self):
        # A flat/collapsed package that is heavy
        assert sort(0, 0, 0, 25) == "SPECIAL"

    def test_zero_volume_one_dim_150(self):
        # Zero volume but one dimension hits 150 → bulky
        assert sort(150, 0, 0, 1) == "SPECIAL"

    def test_very_large_dimensions(self):
        assert sort(10000, 10000, 10000, 1) == "SPECIAL"

    def test_very_large_everything(self):
        assert sort(10000, 10000, 10000, 10000) == "REJECTED"

    def test_float_precision_volume_threshold(self):
        # Carefully chosen floats that land exactly at 1,000,000
        # 125.0 * 100.0 * 80.0 = 1,000,000
        assert sort(125.0, 100.0, 80.0, 1) == "SPECIAL"

    def test_float_precision_just_under_volume(self):
        # 124.99 * 100 * 80 = 999,920 → not bulky
        assert sort(124.99, 100, 80, 1) == "STANDARD"

    def test_integer_inputs(self):
        assert sort(10, 10, 10, 5) == "STANDARD"

    def test_mixed_int_float_inputs(self):
        assert sort(10, 10.5, 10, 5.5) == "STANDARD"


# ---------------------------------------------------------------------------
# 7. Error handling — bad inputs
# ---------------------------------------------------------------------------
class TestErrorHandling:
    def test_negative_width_raises(self):
        with pytest.raises(ValueError, match="width"):
            sort(-1, 10, 10, 5)

    def test_negative_height_raises(self):
        with pytest.raises(ValueError, match="height"):
            sort(10, -1, 10, 5)

    def test_negative_length_raises(self):
        with pytest.raises(ValueError, match="length"):
            sort(10, 10, -1, 5)

    def test_negative_mass_raises(self):
        with pytest.raises(ValueError, match="mass"):
            sort(10, 10, 10, -5)

    def test_string_input_raises(self):
        with pytest.raises(TypeError, match="width"):
            sort("ten", 10, 10, 5)

    def test_none_input_raises(self):
        with pytest.raises(TypeError, match="mass"):
            sort(10, 10, 10, None)

    def test_list_input_raises(self):
        with pytest.raises(TypeError, match="height"):
            sort(10, [10], 10, 5)
