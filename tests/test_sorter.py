"""Classification and validation tests for the package sorter."""

from pathlib import Path

import pytest

import package_sorter
from package_sorter import (
    DIMENSION_THRESHOLD_CM,
    MASS_THRESHOLD_KG,
    REJECTED,
    SPECIAL,
    STANDARD,
    VOLUME_THRESHOLD_CM3,
    __version__,
    sort,
)


def test_package_ships_type_marker() -> None:
    package_dir = Path(package_sorter.__file__).resolve().parent
    assert (package_dir / "py.typed").is_file()


def test_public_contract() -> None:
    assert __version__ == "1.0.0"
    assert STANDARD == "STANDARD"
    assert SPECIAL == "SPECIAL"
    assert REJECTED == "REJECTED"
    assert VOLUME_THRESHOLD_CM3 == 1_000_000
    assert DIMENSION_THRESHOLD_CM == 150
    assert MASS_THRESHOLD_KG == 20


def test_stack_name_is_a_plain_string() -> None:
    result = sort(10, 10, 10, 5)
    assert result == "STANDARD"
    assert type(result) is str


@pytest.mark.parametrize(
    ("width", "height", "length", "mass", "expected"),
    [
        pytest.param(10, 10, 10, 5, "STANDARD", id="small-light"),
        pytest.param(10, 10.5, 10, 5.5, "STANDARD", id="mixed-int-and-float"),
        pytest.param(0.001, 0.001, 0.001, 0.001, "STANDARD", id="tiny-positive"),
        pytest.param(99, 100, 100, 1, "STANDARD", id="volume-just-below"),
        pytest.param(124.99, 100, 80, 1, "STANDARD", id="volume-999920"),
        pytest.param(149, 149, 45, 19.999, "STANDARD", id="just-under-volume-and-mass"),
        pytest.param(149.99, 1, 1, 1, "STANDARD", id="width-just-below-150"),
        pytest.param(1, 149.99, 1, 1, "STANDARD", id="height-just-below-150"),
        pytest.param(1, 1, 149.99, 1, "STANDARD", id="length-just-below-150"),
        pytest.param(1, 1, 1, 19.99, "STANDARD", id="mass-just-below-20"),
        pytest.param(99, 99, 99, 19, "STANDARD", id="below-both-thresholds"),
        pytest.param(100, 100, 100, 1, "SPECIAL", id="volume-exact-light"),
        pytest.param(100, 100, 100, 10, "SPECIAL", id="volume-exact-mass-10"),
        pytest.param(100, 100, 100, 19.99, "SPECIAL", id="volume-exact-not-heavy"),
        pytest.param(100.0, 100.0, 100.0, 1.0, "SPECIAL", id="volume-exact-floats"),
        pytest.param(125, 100, 80, 1, "SPECIAL", id="volume-exact-alternate-factors"),
        pytest.param(101, 100, 100, 1, "SPECIAL", id="volume-just-above"),
        pytest.param(149, 149, 46, 19.999, "SPECIAL", id="volume-just-above-not-heavy"),
        pytest.param(150, 1, 1, 1, "SPECIAL", id="width-exact-150"),
        pytest.param(1, 150, 1, 1, "SPECIAL", id="height-exact-150"),
        pytest.param(1, 1, 150, 1, "SPECIAL", id="length-exact-150"),
        pytest.param(150.001, 1, 1, 1, "SPECIAL", id="width-just-above-150"),
        pytest.param(200, 1, 1, 1, "SPECIAL", id="long-width-small-volume"),
        pytest.param(200, 200, 200, 5, "SPECIAL", id="several-long-sides-light"),
        pytest.param(150, 150, 150, 1, "SPECIAL", id="bulky-by-volume-and-dimension"),
        pytest.param(1e308, 1e308, 1e308, 1, "SPECIAL", id="overflow-volume-light"),
        pytest.param(10**1000, 1, 1, 1, "SPECIAL", id="huge-integer-dimension"),
        pytest.param(10, 10, 10, 20, "SPECIAL", id="mass-exact-20-small"),
        pytest.param(1, 1, 1, 20, "SPECIAL", id="mass-exact-20-unit-cube"),
        pytest.param(1, 1, 1, 100, "SPECIAL", id="mass-well-above-20"),
        pytest.param(99, 99, 99, 20, "SPECIAL", id="heavy-not-bulky"),
        pytest.param(149, 149, 45, 20, "SPECIAL", id="mass-exact-volume-just-below"),
        pytest.param(100, 100, 100, 20, "REJECTED", id="volume-and-mass-exact"),
        pytest.param(100, 100, 100, 50, "REJECTED", id="volume-bulky-heavy"),
        pytest.param(149, 149, 46, 20, "REJECTED", id="volume-just-above-and-heavy"),
        pytest.param(150, 1, 1, 20, "REJECTED", id="width-150-and-heavy"),
        pytest.param(1, 150, 1, 20, "REJECTED", id="height-150-and-heavy"),
        pytest.param(1, 1, 150, 20, "REJECTED", id="length-150-and-heavy"),
        pytest.param(150, 1, 1, 25, "REJECTED", id="dimension-bulky-mass-25"),
        pytest.param(200, 200, 200, 30, "REJECTED", id="several-long-sides-heavy"),
        pytest.param(10_000, 10_000, 10_000, 1, "SPECIAL", id="very-large-light"),
        pytest.param(10_000, 10_000, 10_000, 10_000, "REJECTED", id="very-large-heavy"),
        pytest.param(1e308, 1e308, 1e308, 20, "REJECTED", id="overflow-volume-heavy"),
        pytest.param(10**1000, 1, 1, 20, "REJECTED", id="huge-integer-and-heavy"),
    ],
)
def test_classification(
    width: float,
    height: float,
    length: float,
    mass: float,
    expected: str,
) -> None:
    assert sort(width, height, length, mass) == expected


@pytest.mark.parametrize("field", ["width", "height", "length", "mass"])
@pytest.mark.parametrize(
    ("bad", "error", "detail"),
    [
        pytest.param(0, ValueError, "greater than zero", id="zero"),
        pytest.param(0.0, ValueError, "greater than zero", id="zero-float"),
        pytest.param(-0.0, ValueError, "greater than zero", id="negative-zero"),
        pytest.param(-1, ValueError, "greater than zero", id="negative"),
        pytest.param(-0.01, ValueError, "greater than zero", id="negative-fraction"),
        pytest.param(float("nan"), ValueError, "finite", id="nan"),
        pytest.param(float("inf"), ValueError, "finite", id="infinity"),
        pytest.param(float("-inf"), ValueError, "finite", id="negative-infinity"),
        pytest.param(True, TypeError, "bool", id="true"),
        pytest.param(False, TypeError, "bool", id="false"),
        pytest.param("10", TypeError, "str", id="numeric-string"),
        pytest.param(None, TypeError, "NoneType", id="none"),
        pytest.param([10], TypeError, "list", id="list"),
        pytest.param({"n": 10}, TypeError, "dict", id="dict"),
        pytest.param((10,), TypeError, "tuple", id="tuple"),
        pytest.param(1 + 0j, TypeError, "complex", id="complex"),
    ],
)
def test_rejects_invalid_measurement(
    field: str,
    bad: object,
    error: type[Exception],
    detail: str,
) -> None:
    arguments: dict[str, object] = {
        "width": 10,
        "height": 10,
        "length": 10,
        "mass": 5,
        field: bad,
    }
    with pytest.raises(error, match=field) as exc_info:
        sort(**arguments)  # type: ignore[arg-type]
    message = str(exc_info.value)
    assert detail in message
    if error is ValueError:
        assert str(bad) in message


def test_reports_the_first_invalid_measurement() -> None:
    with pytest.raises(TypeError, match="width must be a number, got str"):
        sort("nope", -1, 0, None)  # type: ignore[arg-type]
