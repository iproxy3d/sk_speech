"""Neutral-profile calibration for pitch features."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

import numpy as np

from .models import NormalizedPitchTrack, PitchTrack


@dataclass(frozen=True, slots=True)
class PitchProfile:
    mean_f0_hz: float
    mean_intensity_db: float
    std_f0_hz: float
    std_intensity_db: float
    voiced_frames: int
    frame_step_s: float

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")
        return output

    @classmethod
    def load(cls, path: str | Path) -> "PitchProfile":
        return cls(**json.loads(Path(path).read_text(encoding="utf-8")))


def calibrate_pitch(track: PitchTrack) -> PitchProfile:
    """Build a neutral profile from voiced frames of a reference recording."""

    mask = track.voiced & np.isfinite(track.f0_hz) & np.isfinite(track.intensity_db)
    if not mask.any():
        raise ValueError("neutral recording contains no usable voiced frames")
    f0 = track.f0_hz[mask]
    intensity = track.intensity_db[mask]
    return PitchProfile(
        mean_f0_hz=float(np.mean(f0)),
        mean_intensity_db=float(np.mean(intensity)),
        std_f0_hz=float(np.std(f0)),
        std_intensity_db=float(np.std(intensity)),
        voiced_frames=int(mask.sum()),
        frame_step_s=track.frame_step_s,
    )


def normalize_pitch(track: PitchTrack, profile: PitchProfile) -> NormalizedPitchTrack:
    """Express F0 and intensity as deviations from the neutral profile."""

    if profile.mean_f0_hz <= 0:
        raise ValueError("profile.mean_f0_hz must be positive")
    f0_delta = track.f0_hz - profile.mean_f0_hz
    f0_relative = f0_delta / profile.mean_f0_hz
    intensity_delta = track.intensity_db - profile.mean_intensity_db
    return NormalizedPitchTrack(
        time_s=track.time_s.copy(),
        f0_relative=f0_relative,
        f0_delta_hz=f0_delta,
        intensity_delta_db=intensity_delta,
        voiced=track.voiced.copy(),
    )

