"""Speech analysis and transformation package.

The frame-aligned F0/intensity API is exported here. Extended analysis and
transformation functions are available in the ``sk_speech.sk_*`` modules.
"""

from .pitch import (
    NormalizedPitchTrack,
    PitchConfig,
    PitchExtractor,
    PitchProfile,
    PitchTrack,
    calibrate_pitch,
    normalize_pitch,
)

__all__ = [
    "NormalizedPitchTrack",
    "PitchConfig",
    "PitchExtractor",
    "PitchProfile",
    "PitchTrack",
    "calibrate_pitch",
    "normalize_pitch",
]

__version__ = "0.1.0"

