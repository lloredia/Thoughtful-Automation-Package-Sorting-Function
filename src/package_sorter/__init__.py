"""Dispatch packages into stacks from their dimensions and mass."""

from package_sorter.sorter import (
    DIMENSION_THRESHOLD_CM,
    MASS_THRESHOLD_KG,
    REJECTED,
    SPECIAL,
    STANDARD,
    VOLUME_THRESHOLD_CM3,
    Stack,
    sort,
)

__all__ = [
    "DIMENSION_THRESHOLD_CM",
    "MASS_THRESHOLD_KG",
    "REJECTED",
    "SPECIAL",
    "STANDARD",
    "VOLUME_THRESHOLD_CM3",
    "Stack",
    "sort",
]

__version__ = "1.0.0"
