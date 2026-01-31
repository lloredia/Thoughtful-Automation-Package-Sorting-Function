"""
Thoughtful Automation — Package Sorting Function
Dispatches packages to the correct stack based on volume and mass.

Stacks:
    STANDARD  — not bulky and not heavy
    SPECIAL   — bulky or heavy (but not both)
    REJECTED  — both bulky and heavy
"""


def sort(width: float, height: float, length: float, mass: float) -> str:
    """
    Determine which stack a package belongs to.

    Args:
        width:  Package width in cm.
        height: Package height in cm.
        length: Package length in cm.
        mass:   Package mass in kg.

    Returns:
        "STANDARD", "SPECIAL", or "REJECTED"

    Raises:
        ValueError: If any dimension or mass is negative.
        TypeError:  If any argument is not a number.
    """
    # --- Input validation ---------------------------------------------------
    for name, value in [("width", width), ("height", height),
                        ("length", length), ("mass", mass)]:
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number, got {type(value).__name__}")
        if value < 0:
            raise ValueError(f"{name} cannot be negative, got {value}")

    # --- Classification logic -----------------------------------------------
    volume = width * height * length

    is_bulky = (volume >= 1_000_000) or any(
        dim >= 150 for dim in (width, height, length)
    )
    is_heavy = mass >= 20

    # --- Dispatch ------------------------------------------------------------
    if is_bulky and is_heavy:
        return "REJECTED"
    if is_bulky or is_heavy:
        return "SPECIAL"
    return "STANDARD"
