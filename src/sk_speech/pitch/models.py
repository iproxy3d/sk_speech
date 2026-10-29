"""Data models for the real-time pitch feature path."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


def _one_dimensional(name: str, value: np.ndarray) -> np.ndarray:
    result = np.asarray(value)
    if result.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    return result


@dataclass(slots=True)
class PitchTrack:
    """Frame-aligned F0 and relative broadband intensity.

    ``intensity_db`` is Praat's intensity estimate for a digital signal.  It is
    not calibrated dB SPL unless the recording chain was calibrated separately.
    Unvoiced F0 values are represented by ``NaN`` and by ``voiced=False``.
    """

    time_s: np.ndarray
    f0_hz: np.ndarray
    intensity_db: np.ndarray
    voiced: np.ndarray
    sample_rate: int
    frame_step_s: float
    duration_s: float

    def __post_init__(self) -> None:
        self.time_s = _one_dimensional("time_s", self.time_s).astype(float, copy=False)
        self.f0_hz = _one_dimensional("f0_hz", self.f0_hz).astype(float, copy=False)
        self.intensity_db = _one_dimensional("intensity_db", self.intensity_db).astype(float, copy=False)
        self.voiced = _one_dimensional("voiced", self.voiced).astype(bool, copy=False)
        lengths = {len(self.time_s), len(self.f0_hz), len(self.intensity_db), len(self.voiced)}
        if len(lengths) != 1:
            raise ValueError("time_s, f0_hz, intensity_db and voiced must have equal lengths")

    def to_csv(self, path: str | Path) -> Path:
        """Write the aligned sequence without requiring pandas."""

        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        values = np.column_stack((self.time_s, self.f0_hz, self.intensity_db, self.voiced.astype(int)))
        np.savetxt(
            output,
            values,
            delimiter=",",
            header="time_s,f0_hz,intensity_db,voiced",
            comments="",
            fmt=["%.9f", "%.9f", "%.9f", "%d"],
        )
        return output


@dataclass(slots=True)
class NormalizedPitchTrack:
    """Pitch sequence expressed relative to a neutral calibration profile."""

    time_s: np.ndarray
    f0_relative: np.ndarray
    f0_delta_hz: np.ndarray
    intensity_delta_db: np.ndarray
    voiced: np.ndarray

    def to_csv(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        values = np.column_stack(
            (
                self.time_s,
                self.f0_relative,
                self.f0_delta_hz,
                self.intensity_delta_db,
                self.voiced.astype(int),
            )
        )
        np.savetxt(
            output,
            values,
            delimiter=",",
            header="time_s,f0_relative,f0_delta_hz,intensity_delta_db,voiced",
            comments="",
            fmt=["%.9f", "%.9f", "%.9f", "%.9f", "%d"],
        )
        return output

