def clamp01(v: float) -> float:
    """
    Clamp and normalize a value to the range [0.0, 1.0].

    Any negative input is converted to positive using abs().
    Values greater than 1.0 are clamped to 1.0.

    This is used to ensure LED brightness values are always valid
    before being sent to the display hardware.
    """
    return max(0.0, min(1.0, abs(v)))

###----------------------