"""Classify packages into dispatch stacks from dimensions and mass."""

import math
from typing import Literal

Stack = Literal["STANDARD", "SPECIAL", "REJECTED"]

STANDARD: Stack = "STANDARD"
SPECIAL: Stack = "SPECIAL"
REJECTED: Stack = "REJECTED"

VOLUME_THRESHOLD_CM3 = 1_000_000
DIMENSION_THRESHOLD_CM = 150
MASS_THRESHOLD_KG = 20


def _require_measurement(name: str, value: object) -> int | float:
    """Return ``value`` when it is a finite number greater than zero.

    Args:
        name: Measurement name used in error messages.
        value: Caller-supplied measurement.

    Returns:
        The same number, once it is known to be usable.

    Raises:
        TypeError: ``value`` is not a real number. Booleans are rejected.
        ValueError: ``value`` is non-finite, zero, or negative.
    """
    # bool is a subclass of int, so it must be rejected before the numeric check.
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"{name} must be a number, got {type(value).__name__}")
    # Integers are always finite. math.isfinite() converts to float and
    # overflows on integers outside the float range.
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number, got {value}")
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero, got {value}")
    return value


def _is_bulky(width: float, height: float, length: float) -> bool:
    """Return whether the package is bulky by volume or by any side.

    Args:
        width: Width in centimeters.
        height: Height in centimeters.
        length: Length in centimeters.

    Returns:
        True when the volume or any single side meets the bulky threshold.
    """
    volume = width * height * length
    return (
        volume >= VOLUME_THRESHOLD_CM3
        or width >= DIMENSION_THRESHOLD_CM
        or height >= DIMENSION_THRESHOLD_CM
        or length >= DIMENSION_THRESHOLD_CM
    )


def sort(width: float, height: float, length: float, mass: float) -> Stack:
    """Classify a package into a dispatch stack.

    A package is bulky when its volume is at least 1,000,000 cm³ or any side
    is at least 150 cm. A package is heavy when its mass is at least 20 kg.
    Packages that are both bulky and heavy are rejected. Packages that are
    only bulky or only heavy are special. The rest are standard.

    Args:
        width: Width in centimeters.
        height: Height in centimeters.
        length: Length in centimeters.
        mass: Mass in kilograms.

    Returns:
        ``STANDARD``, ``SPECIAL``, or ``REJECTED``.

    Raises:
        TypeError: A measurement is not a real number. Booleans are rejected.
        ValueError: A measurement is non-finite, zero, or negative.
    """
    width_cm = _require_measurement("width", width)
    height_cm = _require_measurement("height", height)
    length_cm = _require_measurement("length", length)
    mass_kg = _require_measurement("mass", mass)

    bulky = _is_bulky(width_cm, height_cm, length_cm)
    heavy = mass_kg >= MASS_THRESHOLD_KG
    if bulky and heavy:
        return REJECTED
    if bulky or heavy:
        return SPECIAL
    return STANDARD
